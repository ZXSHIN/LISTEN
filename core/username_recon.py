"""Username Reconnaissance - Check username across 50+ platforms"""

import requests
import threading

PLATFORMS = [
    {"name": "GitHub",        "url": "https://github.com/{}", "err": None},
    {"name": "GitLab",        "url": "https://gitlab.com/{}", "err": None},
    {"name": "Twitter/X",     "url": "https://twitter.com/{}", "err": None},
    {"name": "Instagram",     "url": "https://www.instagram.com/{}/", "err": None},
    {"name": "Reddit",        "url": "https://www.reddit.com/user/{}", "err": "user not found"},
    {"name": "TikTok",        "url": "https://www.tiktok.com/@{}", "err": None},
    {"name": "YouTube",       "url": "https://www.youtube.com/@{}", "err": None},
    {"name": "Pinterest",     "url": "https://www.pinterest.com/{}/", "err": None},
    {"name": "Tumblr",        "url": "https://{}.tumblr.com", "err": None},
    {"name": "Flickr",        "url": "https://www.flickr.com/people/{}", "err": None},
    {"name": "DeviantArt",    "url": "https://www.deviantart.com/{}", "err": None},
    {"name": "SoundCloud",    "url": "https://soundcloud.com/{}", "err": None},
    {"name": "Spotify",       "url": "https://open.spotify.com/user/{}", "err": None},
    {"name": "Steam",         "url": "https://steamcommunity.com/id/{}", "err": "profile not found"},
    {"name": "Twitch",        "url": "https://www.twitch.tv/{}", "err": None},
    {"name": "Patreon",       "url": "https://www.patreon.com/{}", "err": None},
    {"name": "Medium",        "url": "https://medium.com/@{}", "err": None},
    {"name": "Linktree",      "url": "https://linktr.ee/{}", "err": None},
    {"name": "Keybase",       "url": "https://keybase.io/{}", "err": None},
    {"name": "Hackerrank",    "url": "https://www.hackerrank.com/{}", "err": None},
    {"name": "LeetCode",      "url": "https://leetcode.com/{}", "err": None},
    {"name": "Codeforces",    "url": "https://codeforces.com/profile/{}", "err": None},
    {"name": "Behance",       "url": "https://www.behance.net/{}", "err": None},
    {"name": "Dribbble",      "url": "https://dribbble.com/{}", "err": None},
    {"name": "Replit",        "url": "https://replit.com/@{}", "err": None},
    {"name": "Fiverr",        "url": "https://www.fiverr.com/{}", "err": None},
    {"name": "Freelancer",    "url": "https://www.freelancer.com/u/{}", "err": None},
    {"name": "Vimeo",         "url": "https://vimeo.com/{}", "err": None},
    {"name": "Dailymotion",   "url": "https://www.dailymotion.com/{}", "err": None},
    {"name": "Telegram",      "url": "https://t.me/{}", "err": None},
    {"name": "Mastodon",      "url": "https://mastodon.social/@{}", "err": None},
    {"name": "Producthunt",   "url": "https://www.producthunt.com/@{}", "err": None},
    {"name": "Unsplash",      "url": "https://unsplash.com/@{}", "err": None},
    {"name": "About.me",      "url": "https://about.me/{}", "err": None},
    {"name": "Ask.fm",        "url": "https://ask.fm/{}", "err": None},
    {"name": "Wattpad",       "url": "https://www.wattpad.com/user/{}", "err": None},
    {"name": "Goodreads",     "url": "https://www.goodreads.com/{}", "err": None},
    {"name": "Roblox",        "url": "https://www.roblox.com/user.aspx?username={}", "err": None},
    {"name": "Blogger",       "url": "https://{}.blogspot.com", "err": None},
    {"name": "Wordpress",     "url": "https://{}.wordpress.com", "err": None},
    {"name": "StackOverflow", "url": "https://stackoverflow.com/users/{}", "err": None},
    {"name": "HackerNews",    "url": "https://news.ycombinator.com/user?id={}", "err": None},
    {"name": "Gist/GitHub",   "url": "https://gist.github.com/{}", "err": None},
    {"name": "npm",           "url": "https://www.npmjs.com/~{}", "err": None},
    {"name": "PyPI",          "url": "https://pypi.org/user/{}", "err": None},
    {"name": "DockerHub",     "url": "https://hub.docker.com/u/{}", "err": None},
    {"name": "BitBucket",     "url": "https://bitbucket.org/{}", "err": None},
    {"name": "Codepen",       "url": "https://codepen.io/{}", "err": None},
    {"name": "Giphy",         "url": "https://giphy.com/{}", "err": None},
    {"name": "Last.fm",       "url": "https://www.last.fm/user/{}", "err": None},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def _check_single(username, platform, callback):
    url = platform["url"].format(username)
    status = "❓ Unknown"
    try:
        r = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code == 200:
            if platform["err"] and platform["err"].lower() in r.text.lower():
                status = "❌ Not Found"
            else:
                status = "✅ Found"
        elif r.status_code == 404:
            status = "❌ Not Found"
        elif r.status_code == 403:
            status = "🔒 Forbidden"
        elif r.status_code == 429:
            status = "⚠️ Rate Limited"
        else:
            status = f"❓ HTTP {r.status_code}"
    except requests.exceptions.Timeout:
        status = "⏱️ Timeout"
    except Exception:
        status = "❌ Error"

    callback(platform["name"], url, status)


def check_username(username: str, callback, stop_event=None):
    """
    Check username across all platforms.
    callback(platform_name, url, status) called for each result.
    """
    threads = []
    for platform in PLATFORMS:
        if stop_event and stop_event.is_set():
            break
        t = threading.Thread(
            target=_check_single,
            args=(username, platform, callback),
            daemon=True
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join(timeout=15)
