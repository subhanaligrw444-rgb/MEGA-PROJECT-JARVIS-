"""Microphone capture and offline speech recognition using sounddevice + Vosk."""
import json
import queue
import time
from pathlib import Path

import sounddevice as sd
from vosk import KaldiRecognizer, Model, SetLogLevel


class ListenerError(Exception):
    """Raised when the microphone or the speech model cannot be used."""


class Listener:
    def __init__(self, model_path: Path, sample_rate: int = 16000,
                 block_size: int = 4000) -> None:
        if not model_path.exists():
            raise ListenerError(f"Speech model not found: {model_path}")
        SetLogLevel(-1)
        self.sample_rate = sample_rate
        self.block_size = block_size
        self._model = Model(str(model_path))
        self._vocabulary = self._load_vocabulary(model_path)
        self._queue: "queue.Queue[bytes]" = queue.Queue()

    @staticmethod
    def _load_vocabulary(model_path: Path) -> set[str]:
        words_file = model_path / "graph" / "words.txt"
        if not words_file.exists():
            return set()  # cannot filter, so trust the phrase list
        with open(words_file, encoding="utf-8") as file:
            return {line.split()[0] for line in file if line.strip()}

    def _usable_phrases(self, phrases: list[str]) -> list[str]:
        if not self._vocabulary:
            return phrases
        usable = []
        for phrase in phrases:
            missing = [w for w in phrase.split() if w not in self._vocabulary]
            if missing:
                print(f"[grammar] skipped '{phrase}' (unknown words: {missing})")
            else:
                usable.append(phrase)
        return usable

    def _make_recognizer(self, phrases: list[str] | None) -> KaldiRecognizer:
        if phrases:
            grammar = json.dumps(self._usable_phrases(phrases) + ["[unk]"])
            return KaldiRecognizer(self._model, self.sample_rate, grammar)
        return KaldiRecognizer(self._model, self.sample_rate)

    @staticmethod
    def _clean(text: str) -> str:
        return " ".join(w for w in text.lower().split() if w != "[unk]")

    def _callback(self, indata, frames, time_info, status) -> None:
        self._queue.put(bytes(indata))

    def listen(self, timeout: float = 8.0,
               phrases: list[str] | None = None) -> str:
        """Listen for one phrase. With `phrases`, only those phrases can be
        recognized (command mode). Without, any speech is transcribed
        (dictation mode). Returns '' on silence or noise."""
        recognizer = self._make_recognizer(phrases)
        deadline = time.time() + timeout
        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate, blocksize=self.block_size,
                dtype="int16", channels=1, callback=self._callback,
            ):
                self._drain_queue()
                while time.time() < deadline:
                    try:
                        data = self._queue.get(timeout=0.5)
                    except queue.Empty:
                        continue
                    if recognizer.AcceptWaveform(data):
                        text = self._clean(json.loads(recognizer.Result()).get("text", ""))
                        if text:
                            return text
                return self._clean(json.loads(recognizer.FinalResult()).get("text", ""))
        except sd.PortAudioError as error:
            raise ListenerError(f"Microphone problem: {error}") from error

    def _drain_queue(self) -> None:
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break