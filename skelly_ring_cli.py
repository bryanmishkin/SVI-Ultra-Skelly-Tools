import argparse
import base64
import json
import os
import time
from typing import Optional

import requests
from openai import OpenAI
from ring_doorbell import Ring, Auth
from oauthlib.oauth2 import MissingTokenError
import simpleaudio as sa

TOKEN_CACHE = "ring_token.cache"
APP_NAME = "skelly-cli/0.1"


def save_token(token: dict) -> None:
    with open(TOKEN_CACHE, "w") as f:
        json.dump(token, f)


def load_auth() -> Auth:
    """Authenticate with the Ring API using a cached token or credentials."""
    token: Optional[dict] = None
    if os.path.exists(TOKEN_CACHE):
        with open(TOKEN_CACHE) as f:
            token = json.load(f)
    auth = Auth(APP_NAME, token, save_token)
    if token is None:
        username = os.getenv("RING_USERNAME") or input("Ring username: ")
        password = os.getenv("RING_PASSWORD") or input("Ring password: ")
        try:
            auth.fetch_token(username, password)
        except MissingTokenError:
            two_factor = os.getenv("RING_2FA") or input("2FA code: ")
            auth.fetch_token(username, password, two_factor)
    return auth


def connect_ring() -> Ring:
    auth = load_auth()
    ring = Ring(auth)
    ring.update_data()
    return ring


def get_motion_image(doorbell) -> Optional[bytes]:
    """Return snapshot bytes when a new motion event occurs."""
    events = doorbell.history(limit=1, kind="motion")
    if not events:
        return None
    event = events[0]
    event_id = event["id"]
    if getattr(doorbell, "_last_event_id", None) == event_id:
        return None
    doorbell._last_event_id = event_id
    # Fetch a still image from the doorbell
    image = doorbell.get_snapshot()
    if image:
        return image
    # Fallback to downloading first frame of recording
    url = doorbell.recording_download_url(event_id)
    if url:
        return requests.get(url).content
    return None


def generate_heckle(client: OpenAI, image_bytes: bytes) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    prompt = [{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "Make a playful Halloween-themed heckle about this person."},
            {"type": "input_image", "image_base64": b64},
        ],
    }]
    resp = client.responses.create(model="gpt-4.1-mini", input=prompt)
    return resp.output_text.strip()


def speak_text(client: OpenAI, text: str) -> None:
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
        format="wav",
    )
    audio_bytes = speech.audio
    with open("heckle.wav", "wb") as f:
        f.write(audio_bytes)
    wave = sa.WaveObject.from_wave_file("heckle.wav")
    play = wave.play()
    play.wait_done()


def main():
    parser = argparse.ArgumentParser(description="Ring powered heckling for Ultra Skelly")
    parser.add_argument("--poll", type=int, default=5, help="Polling interval in seconds")
    args = parser.parse_args()

    client = OpenAI()
    ring = connect_ring()
    devices = ring.devices()
    if not devices.get("doorbots"):
        raise RuntimeError("No Ring doorbells found")
    doorbell = devices["doorbots"][0]

    print("Waiting for motion events...")
    while True:
        image = get_motion_image(doorbell)
        if image:
            heckle = generate_heckle(client, image)
            print(f"Skelly says: {heckle}")
            speak_text(client, heckle)
        time.sleep(args.poll)


if __name__ == "__main__":
    main()
