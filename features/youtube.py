"""YouTube: find a video for a spoken query and open it in the default browser."""
import webbrowser
from urllib.parse import quote_plus


def results_url(query: str) -> str:
    return "https://www.youtube.com/results?search_query=" + quote_plus(query)


def find_first_video_url(query: str) -> str | None:
    """Ask YouTube for the top result using yt-dlp. Returns None if yt-dlp is
    missing, the network is down, or nothing was found. Nothing is downloaded."""
    try:
        import yt_dlp
    except ImportError:
        return None

    options = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,   # only read search results, do not fetch video data
        "skip_download": True,
        "socket_timeout": 10,
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=False)
    except yt_dlp.utils.DownloadError:
        return None

    entries = (info or {}).get("entries") or []
    video_id = entries[0].get("id") if entries else None
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else None


def play(query: str) -> str:
    """Open the best video, or the results page as a fallback.
    Returns 'video', 'results' or 'failed'."""
    url = find_first_video_url(query)
    if url and webbrowser.open(url):
        return "video"
    if webbrowser.open(results_url(query)):
        return "results"
    return "failed"