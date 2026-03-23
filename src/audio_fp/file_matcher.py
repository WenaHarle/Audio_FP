from __future__ import annotations

import argparse
from pathlib import Path

from .common import check_audio_segment_match_from_file


REPO_ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline audio file matcher.")
    parser.add_argument(
        "--input",
        default=str(REPO_ROOT / "TestFile" / "Oleg_Tamulilingan" / "Test2P.mp3"),
        help="Path to audio segment file.",
    )
    parser.add_argument(
        "--database",
        default=str(REPO_ROOT / "DataBase" / "Oleg.json"),
        help="Path to fingerprint JSON database.",
    )
    parser.add_argument("--threshold", type=float, default=0.01, help="Detection threshold for match ratio.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    is_match, match_ratio = check_audio_segment_match_from_file(
        Path(args.input),
        Path(args.database),
        threshold=args.threshold,
        nperseg=1024,
        noverlap=None,
        window=None,
        peak_threshold=0.5,
        peak_filter_size=20,
        fan_value=15,
    )

    if is_match:
        print(f"MATCH ratio={match_ratio:.8f}")
    else:
        print(f"NO_MATCH ratio={match_ratio:.8f}")


if __name__ == "__main__":
    main()
