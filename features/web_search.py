"""Opens allowlisted websites and web searches in the default browser."""
import webbrowser
from urllib.parse import quote_plus

SITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "wikipedia": "https://www.wikipedia.org",
    "github": "https://www.github.com",
}


def resolve_site(name: str) -> str | None:
    # Vosk may write "you tube", so spaces are removed before lookup.
    return SITES.get(name.replace(" ", "").lower())


def open_site(name: str) -> bool:
    url = resolve_site(name)
    if url is None:
        return False
    return webbrowser.open(url)


def search_web(query: str) -> bool:
    return webbrowser.open("https://www.google.com/search?q=" + quote_plus(query))