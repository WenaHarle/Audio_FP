from __future__ import annotations

import argparse
from pathlib import Path

import serial

from .common import check_audio_segment_match_from_samples, record_audio


REPO_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Real-time microphone matcher with serial output.")
    parser.add_argument("--database", default=str(REPO_ROOT / "DataBase" / "Oleg2.json"), help="Path to fingerprint JSON database.")
    parser.add_argument("--threshold", type=float, default=0.004, help="Detection threshold for match ratio.")
    parser.add_argument("--duration", type=float, default=2.0, help="Recording duration in seconds per loop.")
    parser.add_argument("--sample-rate", type=int, default=44100, help="Audio sample rate for microphone recording.")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port path, for example COM3 on Windows.")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate.")
    parser.add_argument("--no-serial", action="store_true", help="Run detection without sending serial output.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    db_path = Path(args.database)

    if args.no_serial:
        serial_conn = None
    else:
        serial_conn = serial.Serial(args.port, args.baud, timeout=1)

    try:
        while True:
            recorded_samples, recorded_sample_rate = record_audio(duration=args.duration, sample_rate=args.sample_rate)

            is_match, match_ratio = check_audio_segment_match_from_samples(
                recorded_samples,
                recorded_sample_rate,
                db_path,
                threshold=args.threshold,
                nperseg=1024,
                noverlap=None,
                window=None,
                peak_threshold=0.8,
                peak_filter_size=30,
                fan_value=15,
            )

            if is_match:
                print(f"MATCH ratio={match_ratio:.8f}")
                if serial_conn is not None:
                    serial_conn.write(b"1")
            else:
                print(f"NO_MATCH ratio={match_ratio:.8f}")
                if serial_conn is not None:
                    serial_conn.write(b"0")
    except KeyboardInterrupt:
        print("Program interrupted by user.")
    finally:
        if serial_conn is not None and serial_conn.is_open:
            serial_conn.close()
            print("Serial port closed.")


if __name__ == "__main__":
    main()
