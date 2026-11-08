"""Open AI chat websites and hand them the user's question."""
import tkinter
import webbrowser
from urllib.parse import quote_plus

AI_SITES = {
    "chatgpt": {
        "name": "ChatGPT",
        "home": "https://chatgpt.com/",
        "prompt_url": "https://chatgpt.com/?q={q}",
    },
    "claude": {
        "name": "Claude",
        "home": "https://claude.ai/new",
        "prompt_url": "https://claude.ai/new?q={q}",
    },
    "gemini": {
        "name": "Gemini",
        "home": "https://gemini.google.com/app",
        "prompt_url": None,  # no link format we can rely on: clipboard fallback
    },
}

# Spoken forms without spaces. "cloud" is a common mishearing of "claude".
ALIASES = {
    "gpt": "chatgpt", "chatgpt": "chatgpt",
    "claude": "claude", "cloud": "claude",
    "gemini": "gemini",
}


def resolve(name: str) -> str | None:
    return ALIASES.get(name.replace(" ", "").lower())


def copy_to_clipboard(text: str) -> bool:
    try:
        root = tkinter.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # lets Windows take the clipboard contents
        root.destroy()
        return True
    except tkinter.TclError:
        return False


def open_with_prompt(key: str, prompt: str) -> str:
    """Returns 'prefilled', 'clipboard', 'opened' or 'failed'."""
    site = AI_SITES[key]
    if prompt and site["prompt_url"]:
        url = site["prompt_url"].format(q=quote_plus(prompt))
        return "prefilled" if webbrowser.open(url) else "failed"
    copied = bool(prompt) and copy_to_clipboard(prompt)
    if not webbrowser.open(site["home"]):
        return "failed"
    return "clipboard" if copied else "opened"