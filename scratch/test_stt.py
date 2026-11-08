"""Standalone test: microphone -> Vosk -> text. No project code involved."""
import json
import queue
import time
from pathlib import Path

import sounddevice as sd
from vosk import KaldiRecognizer, Model, SetLogLevel

MODEL_PATH = (
    Path(__file__).resolve().parent.parent / "models" / "vosk-model-small-en-us-0.15"
)
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000        # 0.5 seconds of audio per chunk
MAX_SECONDS = 40         # safety limit so the test always ends

audio_queue: "queue.Queue[bytes]" = queue.Queue()


def audio_callback(indata, frames, time_info, status) -> None:
    """Called by sounddevice for every chunk of microphone audio."""
    if status:
        print("Audio status:", status)
    audio_queue.put(bytes(indata))


def main() -> None:
    if not MODEL_PATH.exists():
        print("Model folder not found:", MODEL_PATH)
        return

    SetLogLevel(-1)  # hide Vosk's very noisy internal logging
    print("Loading model (a few seconds)...")
    model = Model(str(MODEL_PATH))
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    print("\nSpeak now. Say 'stop listening' to end the test.")
    print(f"(It also ends automatically after {MAX_SECONDS} seconds.)\n")

    start = time.time()
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        while time.time() - start < MAX_SECONDS:
            data = audio_queue.get()
            if recognizer.AcceptWaveform(data):
                text = json.loads(recognizer.Result()).get("text", "")
                if text:
                    print(f"\nFINAL: {text}")
                    if "stop listening" in text:
                        print("Stop phrase heard. Test finished.")
                        return
            else:
                partial = json.loads(recognizer.PartialResult()).get("partial", "")
                print(f"\r  hearing: {partial:<60}", end="", flush=True)

    print("\nTime limit reached. Test finished.")


if __name__ == "__main__":
    main()