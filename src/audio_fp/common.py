from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import scipy.ndimage as ndi
import sounddevice as sd
from pydub import AudioSegment
from scipy.signal import get_window, stft


HashPoint = Tuple[str, int]


def load_audio(file_path: Path | str) -> Tuple[np.ndarray, int]:
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(44100)
    samples = np.array(audio.get_array_of_samples())
    return samples, audio.frame_rate


def generate_spectrogram(
    samples: np.ndarray,
    sample_rate: int,
    *,
    nperseg: int = 1024,
    noverlap: int | None = None,
    window: str | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    stft_window = get_window(window, nperseg) if window else "hann"
    f, t, zxx = stft(samples, fs=sample_rate, window=stft_window, nperseg=nperseg, noverlap=noverlap)
    return f, t, np.abs(zxx)


def extract_peaks(spectrogram: np.ndarray, *, threshold: float = 0.5, max_filter_size: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    peaks = ndi.maximum_filter(spectrogram, size=max_filter_size) == spectrogram
    peaks &= spectrogram > np.mean(spectrogram) * threshold
    return np.where(peaks)


def generate_hashes(peak_freqs: Sequence[int], peak_times: Sequence[int], *, fan_value: int = 15) -> List[HashPoint]:
    hashes: List[HashPoint] = []
    for i in range(len(peak_freqs)):
        for j in range(1, fan_value):
            if (i + j) < len(peak_freqs):
                freq1 = peak_freqs[i]
                freq2 = peak_freqs[i + j]
                t1 = peak_times[i]
                t2 = peak_times[i + j]
                hash_str = f"{freq1}|{freq2}|{t2 - t1}"
                hash_val = hashlib.sha1(hash_str.encode("utf-8")).hexdigest()
                hashes.append((hash_val, int(t1)))
    return hashes


def load_hashes_from_json(file_path: Path | str) -> List[HashPoint]:
    with open(file_path, "r", encoding="utf-8") as file_obj:
        hashes_dict = json.load(file_obj)
    return hashes_dict["hashes"]


def record_audio(*, duration: float = 2.0, sample_rate: int = 44100) -> Tuple[np.ndarray, int]:
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
    sd.wait()
    print("Recording complete.")
    samples = audio.flatten()
    return samples, sample_rate


def _to_hash_set(hashes: Iterable[HashPoint]) -> set[str]:
    return {hash_item[0] for hash_item in hashes}


def check_audio_segment_match_from_samples(
    samples: np.ndarray,
    sample_rate: int,
    original_hashes_path: Path | str,
    *,
    threshold: float,
    nperseg: int = 1024,
    noverlap: int | None = None,
    window: str | None = None,
    peak_threshold: float = 0.5,
    peak_filter_size: int = 20,
    fan_value: int = 15,
) -> Tuple[bool, float]:
    original_hashes = load_hashes_from_json(original_hashes_path)
    original_hashes_set = _to_hash_set(original_hashes)

    _, _, spectrogram = generate_spectrogram(
        samples,
        sample_rate,
        nperseg=nperseg,
        noverlap=noverlap,
        window=window,
    )
    peak_freqs, peak_times = extract_peaks(
        spectrogram,
        threshold=peak_threshold,
        max_filter_size=peak_filter_size,
    )
    new_hashes = generate_hashes(peak_freqs, peak_times, fan_value=fan_value)
    new_hashes_set = _to_hash_set(new_hashes)

    if not new_hashes_set:
        return False, 0.0

    matches = original_hashes_set.intersection(new_hashes_set)
    match_ratio = len(matches) / len(new_hashes_set)
    return match_ratio >= threshold, match_ratio


def check_audio_segment_match_from_file(
    new_file_path: Path | str,
    original_hashes_path: Path | str,
    *,
    threshold: float,
    nperseg: int = 1024,
    noverlap: int | None = None,
    window: str | None = None,
    peak_threshold: float = 0.5,
    peak_filter_size: int = 20,
    fan_value: int = 15,
) -> Tuple[bool, float]:
    new_samples, new_sample_rate = load_audio(new_file_path)
    return check_audio_segment_match_from_samples(
        new_samples,
        new_sample_rate,
        original_hashes_path,
        threshold=threshold,
        nperseg=nperseg,
        noverlap=noverlap,
        window=window,
        peak_threshold=peak_threshold,
        peak_filter_size=peak_filter_size,
        fan_value=fan_value,
    )
