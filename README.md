# Audio Fingerprint Detection with Microphone and Serial Output

## Overview

This project detects whether an incoming audio segment matches a known reference fingerprint and sends a serial signal based on the result.

It includes:

- Offline file-to-fingerprint matching for testing.
- Real-time microphone capture and matching.
- Serial output integration (for microcontroller or external hardware).
- Precomputed fingerprint databases stored as JSON files.

The implementation uses a spectrogram peak-pair hashing approach similar to classic audio fingerprint pipelines.

## Key Features

- Converts audio to mono, 44.1 kHz for consistent processing.
- Computes STFT spectrograms and extracts local spectral peaks.
- Generates stable SHA-1 hashes from peak pairs.
- Compares live or test hashes with a reference database using match ratio.
- Sends serial value:
  - `1` when match is detected.
  - `0` when no match is detected.

## Project Structure

- `src/audio_fp/`: Main package with reusable modules.
  - `common.py`: Shared fingerprinting and matching functions.
  - `file_matcher.py`: Offline test mode using an audio file segment.
  - `mic_matcher.py`: Real-time microphone matching + serial output.
  - `mic_matcher_tuned.py`: Alternate real-time profile.
  - `serial_smoketest.py`: Minimal serial send smoke test.
- `AudioFingerprintTest.py`: Legacy launcher (kept for compatibility).
- `AudioFingerprintMic.py`: Legacy launcher (kept for compatibility).
- `AudioFingerprintMic2.py`: Legacy launcher (kept for compatibility).
- `sendserial.py`: Legacy launcher (kept for compatibility).
- `DataBase/`: Fingerprint JSON files (`Oleg*.json`).
- `TestFile/`: Sample test inputs for offline matching.
- `requirements.txt`: Python dependency list.
- `.gitignore`: Standard Python and workspace ignores.

## How It Works

1. Audio is loaded or recorded.
2. STFT creates a time-frequency representation.
3. Peak points are extracted from high-energy bins.
4. Peak pairs are converted to hashes from `(freq1, freq2, delta_time)`.
5. New hashes are compared with reference database hashes.
6. Match ratio is computed:

$$
\text{match ratio} = \frac{|H_{new} \cap H_{ref}|}{|H_{new}|}
$$

7. If ratio is above threshold, result is considered a match.

## Requirements

- Python 3.9+
- FFmpeg (required by `pydub` for MP3 and many other formats)
- Audio input device (for microphone modes)
- Serial device (if using hardware output)

Python packages:

- `numpy`
- `pydub`
- `scipy`
- `matplotlib` (used by test script imports)
- `sounddevice`
- `pyserial` (used in code, add if missing)

## Installation

### 1. Create and activate virtual environment (recommended)

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
pip install -e .
```

### 3. Install FFmpeg

- Windows:
  - Install FFmpeg and ensure `ffmpeg.exe` is in your PATH.
  - Verify with `ffmpeg -version`.

## Fingerprint Database Format

Database files are JSON objects with a top-level `hashes` array:

```json
{
  "hashes": [
    ["sha1_hex_hash", 12345],
    ["another_sha1_hex_hash", 12345]
  ]
}
```

- Element `[0]`: SHA-1 hash string.
- Element `[1]`: time index (integer).

Note: Current matching logic compares only hash strings and ignores timestamp alignment.

## Usage

### 1. Offline audio-file check

Use this to validate detection behavior with known test clips.

```powershell
python -m audio_fp.file_matcher
```

Legacy launcher still works:

```powershell
python AudioFingerprintTest.py
```

Edit these values in the script before running:

- `new_audio_segment_path`
- `original_hashes_path`
- `threshold`

### 2. Real-time microphone check with serial output

```powershell
python -m audio_fp.mic_matcher
```

or

```powershell
python -m audio_fp.mic_matcher_tuned
```

Legacy launchers still work:

```powershell
python AudioFingerprintMic.py
python AudioFingerprintMic2.py
```

Both scripts continuously:

- Record short audio windows (default 2 seconds).
- Compute and compare hashes.
- Send serial output (`1` or `0`).

Stop with `Ctrl + C`.

### 3. Serial send smoke test

```powershell
python -m audio_fp.serial_smoketest
```

Legacy launcher still works:

```powershell
python sendserial.py
```

### Optional CLI examples

```powershell
python -m audio_fp.mic_matcher --database DataBase/Oleg2.json --port COM3 --threshold 0.004
python -m audio_fp.mic_matcher_tuned --database DataBase/Oleg6.json --port COM3 --threshold 0.009
python -m audio_fp.file_matcher --input TestFile/Oleg_Tamulilingan/Test2P.mp3 --database DataBase/Oleg.json
python -m audio_fp.serial_smoketest --port COM3 --payload 1
```

## Configuration Guide

Tune these values based on room noise, microphone quality, and target audio:

- `threshold` in `check_audio_segment_match(...)`
  - Higher value: stricter matching, fewer false positives.
  - Lower value: more sensitive, potentially more false positives.
- `duration` in `record_audio(...)`
  - Longer windows can improve confidence but increase latency.
- Peak extraction settings:
  - `threshold` argument in `extract_peaks(...)`
  - `maximum_filter` window size
- Hash pairing density:
  - `fan_value` in `generate_hashes(...)`

## Serial Port Setup Notes

Current scripts use Linux-style port path:

- `/dev/ttyUSB0`

On Windows, update to your COM port (for example `COM3`):

```python
ser = serial.Serial('COM3', 115200, timeout=1)
```

Also verify baud rate and timeout match your hardware firmware.

## Operational Notes

- The repository currently includes matcher scripts and precomputed databases.
- A dedicated database-generation script is not included in this repository state.
- `AudioFingerprintMic2.py` uses modified STFT/peak/hash parameters compared to `AudioFingerprintMic.py` for alternate tuning.

## Troubleshooting

### `pydub` cannot decode MP3

- Ensure FFmpeg is installed and available in PATH.
- Restart terminal after PATH changes.

### No microphone input or device errors

- Confirm recording permissions in OS settings.
- Test `sounddevice` with a small recording snippet.
- Verify sample rate support (44.1 kHz).

### Serial port cannot open

- Verify correct port name (`COMx` on Windows).
- Close other apps using the same port.
- Check cable/driver and baud rate.

### Match ratio is always low

- Use cleaner audio environment.
- Increase recording duration.
- Lower threshold slightly.
- Ensure reference database corresponds to the same source track version.

## Security and Safety

- Validate serial payload handling on connected hardware.
- Avoid running with elevated privileges unless required by your environment.

## Future Improvements

- Add a fingerprint database generation tool from source audio.
- Add timestamp-offset consistency checks for stronger matching.
- Add CLI arguments instead of hard-coded paths.
- Add structured logging and benchmark scripts.
- Add automated tests for detection thresholds and regression checks.
