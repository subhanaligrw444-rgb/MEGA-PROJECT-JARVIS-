import unittest

from core.command_router import CommandRouter


class RouterTests(unittest.TestCase):
    
    def test_youtube_play(self):
        self.check("play despacito", "play_youtube", query="despacito")
        self.check("play music", "play_youtube", query="")
        self.check("can you play shape of you on youtube",
                   "play_youtube", query="shape of you")
        self.check("search youtube for cats", "play_youtube", query="cats")
    def setUp(self):
        self.router = CommandRouter()

    def check(self, text, name, **args):
        intent = self.router.parse(text)
        self.assertEqual(intent.name, name, f"'{text}' -> {intent}")
        for key, value in args.items():
            self.assertEqual(intent.args.get(key), value, f"'{text}' -> {intent}")

    def test_open_phrasings_give_same_intent(self):
        for text in ("open youtube", "jarvis open youtube",
                     "can you launch youtube", "please open the youtube"):
            with self.subTest(text=text):
                self.check(text, "open_site", target="youtube")

    def test_split_site_name_is_kept_for_lookup(self):
        self.check("open you tube", "open_site", target="you tube")

    def test_greetings_and_misheard_wake_word(self):
        self.check("hello", "greeting")
        self.check("hello jarvis", "greeting")
        self.check("hello drivers", "greeting")
        self.check("jarvis", "greeting", wake_only=True)

    def test_time_date_day(self):
        self.check("what time is it", "time")
        self.check("what time is it jarvis", "time")
        self.check("what is the date", "date")
        self.check("what day is it", "day")

    def test_whole_word_matching(self):
        self.check("sometime tomorrow maybe", "unknown")

    def test_search(self):
        self.check("search for python tutorials", "search_web",
                   query="python tutorials")
        self.check("google cats", "search_web", query="cats")

    def test_exit(self):
        for text in ("goodbye", "exit", "jarvis quit", "stop listening"):
            with self.subTest(text=text):
                self.check(text, "exit")

    def test_unknown_and_noise(self):
        self.check("i know", "unknown")
        self.check("but bad", "unknown")

    def test_wikipedia_not_yet_supported(self):
        # Wikipedia is the next feature. Until then it must not become a web search.
        self.check("search wikipedia for python", "unknown")

    def test_search_without_query(self):
        self.check("search the web", "search_web", query="")

if __name__ == "__main__":
    unittest.main()