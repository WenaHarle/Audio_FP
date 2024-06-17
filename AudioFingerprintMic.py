import numpy as np
from pydub import AudioSegment
from scipy.signal import stft
import scipy.ndimage as ndi
import hashlib
import json
import matplotlib.pyplot as plt
import sounddevice as sd

def load_audio(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(44100)
    samples = np.array(audio.get_array_of_samples())
    return samples, audio.frame_rate

def generate_spectrogram(samples, sample_rate):
    f, t, Zxx = stft(samples, fs=sample_rate, nperseg=1024)
    return f, t, np.abs(Zxx)

def extract_peaks(spectrogram, threshold=0.5):
    peaks = ndi.maximum_filter(spectrogram, size=20) == spectrogram
    peaks &= spectrogram > np.mean(spectrogram) * threshold
    return np.where(peaks)

def generate_hashes(peak_freqs, peak_times, fan_value=15):
    hashes = []
    for i in range(len(peak_freqs)):
        for j in range(1, fan_value):
            if (i + j) < len(peak_freqs):
                freq1 = peak_freqs[i]
                freq2 = peak_freqs[i + j]
                t1 = peak_times[i]
                t2 = peak_times[i + j]
                hash_str = f"{freq1}|{freq2}|{t2 - t1}"
                hash_val = hashlib.sha1(hash_str.encode('utf-8')).hexdigest()
                hashes.append((hash_val, int(t1)))
    return hashes

def load_hashes_from_json(file_path):
    with open(file_path, "r") as f:
        hashes_dict = json.load(f)
    return hashes_dict["hashes"]

def record_audio(duration=2, sample_rate=44100):
    print("Recording...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()
    print("Recording complete.")
    samples = audio.flatten()
    return samples, sample_rate

def check_audio_segment_match(samples, sample_rate, original_hashes_path, threshold=0.01):
    original_hashes = load_hashes_from_json(original_hashes_path)
    original_hashes_set = set([h[0] for h in original_hashes])
    
    f, t, new_spectrogram = generate_spectrogram(samples, sample_rate)
    peak_freqs, peak_times = extract_peaks(new_spectrogram)
    new_hashes = generate_hashes(peak_freqs, peak_times)
    
    new_hashes_set = set([h[0] for h in new_hashes])
    matches = original_hashes_set.intersection(new_hashes_set)
    
    match_ratio = len(matches) / len(new_hashes_set)
    return match_ratio >= threshold, match_ratio

if __name__ == "__main__":
    # Record a 2-second audio segment from the microphone
    recorded_samples, recorded_sample_rate = record_audio()
    
    # Path to the original hashes JSON file
    original_hashes_path = "DataBase/Oleg.json"
    
    # Check if the recorded audio segment matches any part of the original song
    is_match, match_ratio = check_audio_segment_match(recorded_samples, recorded_sample_rate, original_hashes_path)
    
    if is_match:
        print(f"The audio segment matches part of the original song with a match ratio of {match_ratio:.8f}.")
    else:
        print(f"The audio segment does not match any part of the original song. Match ratio: {match_ratio:.8f}.")
