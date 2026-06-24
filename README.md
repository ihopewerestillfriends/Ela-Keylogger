# Keylogger (Discord Webhook)

## Overview
A Python keylogger

## Features
- Captures keyboard input (via `pynput`)
- Batches up to `MAX_BATCH_SIZE` keystrokes or sends every `BATCH_INTERVAL` seconds
- Sends payloads to a Discord webhook (`WEBHOOK_URL`)
- Appends errors/failures to `keylog.txt` as a local fallback

## Setup
1. Install dependencies:
   - `pip install pynput requests`
2. Edit `WEBHOOK_URL` in `main.py`.

## Run
- `python main.py`

