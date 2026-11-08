"""The list of phrases Jarvis listens for in command mode."""
from features.web_search import SITES

# Vosk often splits brand names, so we also list the spoken form.
SPOKEN_VARIANTS = {"youtube": ["you tube"]}

FIXED_COMMANDS = [
    "hello", "hi", "hey", "hello jarvis", "jarvis",
    "goodbye", "exit", "quit", "bye", "stop listening",
    "what time is it", "what is the time", "what is the date",
    "what day is it", "what is today",
    "search the web", "search google",
      "play music", "play a song", "play song", "play video",
    "play something", "play on youtube", "search youtube",
     "open gpt", "open chat gpt", "open claude", "open gemini",
    "launch gpt", "launch claude", "launch gemini",
]


def build_command_phrases() -> list[str]:
    phrases = set(FIXED_COMMANDS)
    for site in SITES:
        for spoken in [site, *SPOKEN_VARIANTS.get(site, [])]:
            phrases.add(f"open {spoken}")
            phrases.add(f"launch {spoken}")
    # Allow every phrase with "jarvis" in front, e.g. "jarvis open google".
    phrases |= {f"jarvis {phrase}" for phrase in list(phrases) if "jarvis" not in phrase}
    return sorted(phrases)