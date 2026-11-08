"""Assistant lifecycle: listen -> route -> execute -> speak -> repeat."""
from core.command_router import CommandRouter, Intent
from core.listener import Listener, ListenerError
from core.speaker import Speaker
from features import time_info, web_search
from core.vocabulary import build_command_phrases
from features import time_info, web_search, youtube 
from features import ai_sites, time_info, web_search, youtube

CANCEL_WORDS = {"no", "nothing", "cancel", "never mind", "nope"}

class Assistant:
    def __init__(self, config: dict, listener: Listener, speaker: Speaker) -> None:
        self.config = config
        self.listener = listener
        self.speaker = speaker
        self.router = CommandRouter()
        self.command_phrases = build_command_phrases()
        self._handlers = {
            "greeting": self._greeting,
            "time": lambda intent: time_info.time_text(),
            "date": lambda intent: time_info.date_text(),
            "day": lambda intent: time_info.day_text(),
            "open_site": self._open_site,
            "search_web": self._search_web,
            "play_youtube": self._play_youtube,
            "open_ai": self._open_ai,
            "unknown": self._unknown,

        }

    def _open_ai(self, intent: Intent) -> str:
        key = intent.args["site"]
        name = ai_sites.AI_SITES[key]["name"]
        self.speaker.speak(f"Opening {name}. What would you like to ask?")
        question = self.listener.listen(12)  # dictation mode: any words
        if question in CANCEL_WORDS:
            question = ""
        print(f"[ai] question: {question!r}")

        result = ai_sites.open_with_prompt(key, question)
        if result == "prefilled":
            return f"I put your question into {name}."
        if result == "clipboard":
            return f"{name} is open. Your question is copied, so press Control V to paste it."
        if result == "opened":
            return f"{name} is open."
        return "I could not open the browser."

    def run(self) -> None:
        name = self.config["assistant_name"]
        self.speaker.speak(f"{name} is online. I am listening.")
        try:
            while True:
                try:
                                        text = self.listener.listen(
                        self.config["listen_timeout_seconds"], self.command_phrases
                    )
                except ListenerError as error:
                    print(error)
                    self.speaker.speak("I cannot access the microphone.")
                    break

                if not text:
                    continue
                print(f"You: {text}")

                intent = self.router.parse(text)
                if intent.name == "exit":
                    self.speaker.speak("Goodbye.")
                    break

                reply = self.execute(intent)
                if reply:
                    self.speaker.speak(reply)
        except KeyboardInterrupt:
            print("\nStopped with Ctrl+C.")

    def execute(self, intent: Intent) -> str:
        handler = self._handlers.get(intent.name)
        return handler(intent) if handler else ""

    def _greeting(self, intent: Intent) -> str:
        if intent.args.get("wake_only"):
            return "Yes? I am listening."
        return "Hello. How can I help you?"

    def _open_site(self, intent: Intent) -> str:
        target = intent.args["target"]
        if web_search.open_site(target):
            return f"Opening {target}."
        return f"I do not know how to open {target} yet."

    def _search_web(self, intent: Intent) -> str:
        query = intent.args.get("query", "")
        if not query:
            self.speaker.speak("What should I search for?")
            query = self.listener.listen(10)  # dictation mode: any words
            if not query:
                return "I did not hear a search phrase."
        web_search.search_web(query)
        return f"Searching the web for {query}."

    def _unknown(self, intent: Intent) -> str:
        # One-word results are usually noise, so stay silent instead of nagging.
        if len(intent.args.get("text", "").split()) < 2:
            return ""
        return "Sorry, I did not understand that. Please try again."
    
    def _play_youtube(self, intent: Intent) -> str:
        query = intent.args.get("query", "")
        if not query:
            self.speaker.speak("Which song or video?")
            query = self.listener.listen(10)  # dictation mode: any words
            if not query:
                return "I did not hear a song name."
        self.speaker.speak(f"Looking for {query} on YouTube.")
        result = youtube.play(query)
        if result == "video":
            return "Opening it now."
        if result == "results":
            return "I could not pick a video, so I opened the YouTube results."
        return "I could not open the browser."
    
    def test_open_ai_sites(self):
        for text in ("open gpt", "jarvis open chat gpt", "can you launch chatgpt"):
            with self.subTest(text=text):
                self.check(text, "open_ai", site="chatgpt")
        self.check("open claude", "open_ai", site="claude")
        self.check("open cloud", "open_ai", site="claude")
        self.check("open google", "open_site", target="google")