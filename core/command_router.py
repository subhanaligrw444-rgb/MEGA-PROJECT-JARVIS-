"""Turns recognized speech into an Intent. No audio here, so it is easy to test."""
import re
from dataclasses import dataclass, field
from features import ai_sites

# Words Vosk may produce when we say "Jarvis". Add more as we observe them.
WAKE_WORDS = {"jarvis", "drivers", "service", "travis", "javis", "jarvas"}
GREETING_WORDS = {"hello", "hi", "hey"}
POLITE_PREFIXES = (
    "can you", "could you", "would you", "will you",
    "please", "go ahead and", "i want you to",
)
EXIT_COMMANDS = {"exit", "quit", "goodbye", "good bye", "bye", "stop listening"}

OPEN_SYNONYMS = re.compile(r"^(launch|go to|take me to|pull up)\b")
OPEN_RE = re.compile(r"^open\s+(.+)$")
SEARCH_RE = re.compile(
    r"^(?:search(?: the web| google| online)?(?: for)?|google|look up)"
    r"(?:\s+(?!wikipedia\b)(.+))?$"
)
DAY_RE = re.compile(r"\bwhat day\b|\bday of the week\b|^what is today$")
DATE_RE = re.compile(r"\bdate\b")
TIME_RE = re.compile(r"\btime\b")

PLAY_RE = re.compile(
    r"^play(?:\s+(?:a|some|the))?(?:\s+(?:song|songs|music|video))?(?:\s+(.+))?$"
)
YT_SEARCH_RE = re.compile(r"^search youtube(?:\s+for)?(?:\s+(.+))?$")


@dataclass
class Intent:
    name: str
    args: dict = field(default_factory=dict)


def normalize(text: str) -> tuple[str, bool, bool]:
    """Clean the text. Returns (command, was_greeted, wake_word_heard)."""
    words = re.sub(r"[^a-z0-9' ]", " ", text.lower()).split()

    greeted = False
    if words and words[0] in GREETING_WORDS:
        greeted = True
        words = words[1:]

    woke = False
    if words and words[0] in WAKE_WORDS:
        woke = True
        words = words[1:]
    elif len(words) > 1 and words[-1] == "jarvis":
        woke = True
        words = words[:-1]

    command = " ".join(words)
    changed = True
    while changed:  # remove stacked politeness: "please can you ..."
        changed = False
        for prefix in POLITE_PREFIXES:
            if command == prefix or command.startswith(prefix + " "):
                command = command[len(prefix):].strip()
                changed = True

    command = OPEN_SYNONYMS.sub("open", command)
    command = re.sub(r"^open the ", "open ", command)
    return command, greeted, woke


class CommandRouter:
    def parse(self, text: str) -> Intent:
        command, greeted, woke = normalize(text)

        if not command:
            if greeted:
                return Intent("greeting")
            if woke:
                return Intent("greeting", {"wake_only": True})
            return Intent("unknown", {"text": text})

        if command in EXIT_COMMANDS:
            return Intent("exit")

        match = OPEN_RE.match(command)
        if match:
            site_key = ai_sites.resolve(match.group(1))
            if site_key:
                return Intent("open_ai", {"site": site_key})
            return Intent("open_site", {"target": match.group(1)})

        match = YT_SEARCH_RE.match(command) or PLAY_RE.match(command)
        if match:
            query = re.sub(r"\s+on youtube$", "", match.group(1) or "")
            return Intent("play_youtube", {"query": query})
        

        match = SEARCH_RE.match(command)
        if match:
            return Intent("search_web", {"query": match.group(1) or ""})

        if DAY_RE.search(command):
            return Intent("day")
        if DATE_RE.search(command):
            return Intent("date")
        if TIME_RE.search(command):
            return Intent("time")

        return Intent("unknown", {"text": text})