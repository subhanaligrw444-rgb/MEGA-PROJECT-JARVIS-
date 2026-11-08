"""Jarvis entry point."""
import json
from pathlib import Path

from core.assistant import Assistant
from core.listener import Listener, ListenerError
from core.speaker import Speaker

BASE_DIR = Path(__file__).resolve().parent


def load_config() -> dict:
    with open(BASE_DIR / "config" / "config.json", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    config = load_config()
    speaker = Speaker(config["speech_rate"], config["speech_volume"])
    try:
        listener = Listener(BASE_DIR / config["model_path"], config["sample_rate"])
    except ListenerError as error:
        print(error)
        return
    Assistant(config, listener, speaker).run()


if __name__ == "__main__":
    main()