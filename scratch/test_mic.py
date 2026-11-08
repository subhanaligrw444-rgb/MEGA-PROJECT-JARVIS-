import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Vosk models expect 16 kHz audio
SECONDS = 4

print("=== Audio devices ===")
print(sd.query_devices())
print()
print("Default (input, output):", sd.default.device)
print()

print(f"Recording {SECONDS} seconds... SPEAK NOW, say anything.")
recording = sd.rec(
    int(SECONDS * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
)
sd.wait()  # block until recording is finished

peak = int(np.abs(recording).max())
print(f"Peak volume: {peak} (max possible 32767)")

if peak < 200:
    print("RESULT: Almost silent. Wrong device, muted mic, or permission blocked.")
elif peak < 1500:
    print("RESULT: Very quiet. Mic works but speak louder or raise input volume.")
else:
    print("RESULT: Microphone is working.")