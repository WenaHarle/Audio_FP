from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from audio_fp.serial_smoketest import main


if __name__ == "__main__":
    main()
