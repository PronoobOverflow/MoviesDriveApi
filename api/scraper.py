import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from threading import Lock
import re
import time
import hashlib
import secrets
import pyshorteners
from urllib.parse import quote

# Mirrors
BASE_URLS = [
    "https://pronoobdrive-piya-ja-c-ky-j-a-sp-e-r-9.onrender.com",
    "https://pronoobdrive.onrender.com",
    "https://pronoobdrive-7w2p.onrender.com"
]

TIMEOUT = 30
SECRET_KEY = "supersecretkey"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Initialize URL shortener
s = pyshorteners.Shortener()

# Get active mirrors
def get_active_urls():
    active = []
    for url in BASE_URLS:
        try:
            test_url = f"{url}/Sct?search=test"
            res = requests.get(test_url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, 'html.parser')
            # Check for any movie link
            if res.status_code == 200 and soup.select_one('a[href*="/Sct/"]'):
                active.append(url)
        except Exception as e:
            print(f"[CHECK FAIL] {url} - {e}")
    return active

ACTIVE_URLS = get_active_urls()
if not ACTIVE_URLS:
    raise Exception("All base URLs are down. Please try again later.")

print(f"[INFO] Active Mirrors: {ACTIVE_URLS}")

# Mirror rotation (thread-safe)
mirror_cycle = cycle(ACTIVE_URLS)
mirror_lock = Lock()

def get_next_mirror():
    with mirror_lock:
        return next(mirror_cycle)

# Temporary link generator
def generate_temp_link(original_link):
    expires = int(time.time()) + 25200  # 7 hours
    random_str = secrets.token_hex(8)
    data = f"{original_link}|{expires}|{random_str}"
    token = hashlib.sha256(f"{data}{SECRET_KEY}".encode()).hexdigest()
    temp_link = f"https://pronoob-drive.vercel.app/api/redirect?file={quote(original_link)}&expires={expires}&token={token}&hash={random_str}"
    return s.tinyurl.short(temp_link)

# Get file size from HEAD request
def get_file_size(url):
    try:
        with requests.head(url, headers=HEADERS, timeout=10) as response:
            size_bytes = int(response.headers.get('content-length', 0))
            if size_bytes == 0:
                return "Unknown size"
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size_bytes < 1024.0:
                    return f"{size_bytes:.2f} {unit}"
                size_bytes /= 1024.0
            return f"{size_bytes:.2f} TB"
    except Exception as e:
        print(f"[WARN] Couldn't get size for {url}: {e}")
        return "Unknown size"

# Scrape download links from movie page
def fetch_links(chosen_mirror, movie_href, title):
    try:
        movie_page = f"{chosen_mirror}{movie_href}"
        res = requests.get(movie_page, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()

        if "bandwidth" in res.text.lower() and "exceeded" in res.text.lower():
            raise Exception("Bandwidth limit exceeded")

        soup = BeautifulSoup(res.text, "html.parser")
        video_links = []

        for tag in soup.select('a[href]'):
            href = tag['href']
            if any(href.endswith(ext) for ext in [".mkv", ".mp4", ".avi"]):
                full_url = chosen_mirror + href
                size = get_file_size(full_url)
                temp_link = generate_temp_link(full_url)
                video_links.append({
                    "url": temp_link,
                    "size": size
                })

        if not video_links:
            size = get_file_size(movie_page)
            temp_link = generate_temp_link(movie_page)
            video_links.append({
                "url": temp_link,
                "size": size
            })

        return {
            "title": title,
            "links": video_links
        }

    except Exception as e:
        print(f"[WARN] Failed on {chosen_mirror} for {title}: {str(e)}")
        return None

# Helpers
def tokenize_string(s):
    return re.findall(r'\w+', s.lower())

def extract_season_code(s):
    match = re.search(r'(s\d{2})', s.lower())
    return match.group(1) if match else ""

# Main search handler
def get_all_movie_links(movie_name):
    try:
        movie_name = ' '.join(word.capitalize() for word in movie_name.split())  # Capitalize each word
        chosen_mirror = get_next_mirror()
        search_url = f"{chosen_mirror}/Sct?search={movie_name.replace(' ', '+')}"
        res = requests.get(search_url, headers=HEADERS, timeout=TIMEOUT)
        res.raise_for_status()

        if "bandwidth" in res.text.lower() and "exceeded" in res.text.lower():
            raise Exception("Bandwidth limit exceeded")

        soup = BeautifulSoup(res.text, "html.parser")
        search_keywords = tokenize_string(movie_name)
        season_code = extract_season_code(movie_name)

        tasks = []
        href_blocks = soup.select('a[href*="/Sct/"]')

        for block in href_blocks:
            href = block['href']
            title_tag = block.find_next("div", class_="p-2")
            raw_title = title_tag.text.strip() if title_tag else ""
            combined_tokens = tokenize_string(f"{raw_title} {href}")

            match_count = sum(1 for keyword in search_keywords if keyword in combined_tokens)
            if match_count > 0 or (season_code and season_code in ''.join(combined_tokens)):
                tasks.append((chosen_mirror, href, raw_title.title() or href))

        results = []
        with ThreadPoolExecutor(max_workers=25) as executor:
            for result in executor.map(lambda args: fetch_links(*args), tasks):
                if result:
                    results.append(result)

        return {
            "mirror_used": chosen_mirror,
            "data": results
        }

    except Exception as e:
        print(f"[ERROR] Search failed: {str(e)}")
        return {"error": str(e)}
