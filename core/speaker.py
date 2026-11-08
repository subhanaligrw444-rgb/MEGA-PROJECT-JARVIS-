"""Text-to-speech using the offline Windows voices through pyttsx3."""
import pyttsx3


class Speaker:
    """Speaks text aloud. speak() blocks until the speech has finished."""

    def __init__(self, rate: int = 175, volume: float = 1.0) -> None:
        self.rate = rate
        self.volume = volume

    def speak(self, text: str) -> None:
        if not text:
            return
        print(f"Jarvis: {text}")
        # A fresh engine per call avoids a known pyttsx3 problem on Windows,
        # where the engine can go silent after the first runAndWait().
        engine = pyttsx3.init()
        try:
            engine.setProperty("rate", self.rate)
            engine.setProperty("volume", self.volume)
            engine.say(text)
            engine.runAndWait()
        finally:
            engine.stop()