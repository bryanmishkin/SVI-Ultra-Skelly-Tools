# SVI-Ultra-Skelly-Tools

Sample code for externally controlling the [SVI App Controlled Ultra Skeleton](https://www.homedepot.com/p/Home-Accents-Holiday-6-5-ft-Grave-Bones-Animated-LED-App-Controlled-Ultra-Skelly-with-LifeEyes-LCD-Eyes-H23-25SV24690/333508046).

This project is experimental and many features have not been fully tested. Use at your own risk and feel free to contribute improvements.

## Getting Started

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Provide credentials**

   - `OPENAI_API_KEY` – API key for ChatGPT.
   - `RING_USERNAME` and `RING_PASSWORD` – Ring account credentials. The first run will prompt for a 2FA code and create a `ring_token.cache` file for reuse.

3. **Run the Ring/Skeleton CLI**

   ```bash
   python skelly_ring_cli.py
   ```

   The CLI watches for motion from your Ring camera. When motion is detected it retrieves an image, asks ChatGPT for a playful heckle, and has the skeleton speak the line. The script waits until the audio finishes before monitoring for the next event.

## Contributions

I'll continue to add features and fix bugs, but any additional help is greatly appreciated!
