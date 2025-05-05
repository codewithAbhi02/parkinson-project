import parselmouth
import numpy as np

def extract_features(file_path):
    sound = parselmouth.Sound(file_path)
    pitch = sound.to_pitch()
    point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 500)

    # Basic Jitter & Shimmer
    jitter_local = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    jitter_rap = parselmouth.praat.call(point_process, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
    jitter_ppq5 = parselmouth.praat.call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)

    shimmer_local = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_apq3 = parselmouth.praat.call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    shimmer_apq5 = parselmouth.praat.call([sound, point_process], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)

    # HNR (Harmonics-to-Noise Ratio)
    hnr = parselmouth.praat.call(sound, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
    hnr_mean = parselmouth.praat.call(hnr, "Get mean", 0, 0)

    # Pitch features
    pitch_values = pitch.selected_array['frequency']
    pitch_values = pitch_values[pitch_values != 0]  # remove unvoiced
    pitch_mean = np.mean(pitch_values) if len(pitch_values) > 0 else 0
    pitch_std = np.std(pitch_values) if len(pitch_values) > 0 else 0
    pitch_min = np.min(pitch_values) if len(pitch_values) > 0 else 0
    pitch_max = np.max(pitch_values) if len(pitch_values) > 0 else 0

    return {
        "jitter_local": jitter_local,
        "jitter_rap": jitter_rap,
        "jitter_ppq5": jitter_ppq5,
        "shimmer_local": shimmer_local,
        "shimmer_apq3": shimmer_apq3,
        "shimmer_apq5": shimmer_apq5,
        "hnr_mean": hnr_mean,
        "pitch_mean": pitch_mean,
        "pitch_std": pitch_std,
        "pitch_min": pitch_min,
        "pitch_max": pitch_max,
    }


