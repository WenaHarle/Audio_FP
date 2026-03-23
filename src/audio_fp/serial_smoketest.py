from __future__ import annotations

import argparse
import time

import serial


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send a one-byte payload over serial for smoke testing.")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port path, for example COM3 on Windows.")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate.")
    parser.add_argument("--payload", default="0", help="Payload string to send.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    with serial.Serial(args.port, args.baud, timeout=1) as serial_conn:
        time.sleep(0.01)
        serial_conn.write(args.payload.encode())
    print("Serial payload sent.")


if __name__ == "__main__":
    main()
