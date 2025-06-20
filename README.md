# 🎬 Movies Drive API

A fast, Python-based movie scraper API that fetches download links from multiple mirrors. The API supports concurrency, encrypted links, Cloudflare Worker proxying, and short URL generation (like TinyURL).

---

## 🚀 Features

- 🔍 Movie search and auto mirror fallback  
- 🌐 Multiple rotating mirror support (`pronoobdrive`)  
- ⚡ High-speed concurrent scraping  
- 🔒 Encrypted download links for safe distribution  
- 📏 Download size included  
- 🔗 URL shortening via **TinyURL**  
- ☁️ Cloudflare Worker proxy support for faster, safer link delivery  

---

## 🛠️ Tech Stack

- Python 3.x  
- `requests`, `BeautifulSoup`  
- `concurrent.futures.ThreadPoolExecutor`  
- `hashlib`, `secrets` for encryption  
- `pyshorteners` for TinyURL support  
- Cloudflare Workers (optional but recommended)  

---

## 📦 Installation

```bash
git clone https://github.com/your-username/MoviesDriveAPI.git
cd MoviesDriveAPI
pip install -r requirements.txt
python app.py
```

Update `BASE_URLS` with active mirror links.

---

## 🧪 How It Works

1. Accepts movie name as input.  
2. Rotates through multiple mirrors.  
3. Scrapes and extracts all matching download links + size + quality.  
4. Encrypts each link for security.  
5. Optionally shortens it using TinyURL.  
6. Returns links, optionally passed through a Cloudflare Worker for delivery.  

---

## 🌐 Example Endpoint

### `GET /search?query=movie+name`

**Response:**

```json
{
  "title": "Movie Name",
  "results": [
    {
      "quality": "1080p",
      "size": "1.2GB",
      "link": "https://autumn-truth-1dd3.genuinetvlive.workers.dev/temp-encrypted-id"
    },
    {
      "quality": "720p",
      "size": "950MB",
      "link": "https://tinyurl.com/shortened-link"
    }
  ]
}
```

---

## 🔐 Encryption Logic

Links are encrypted using a combination of:
- Random salts  
- HMAC or hash-based tokens  
- TTL (optional) logic to make them expire  

This protects direct download access and discourages scraping or overuse.

---

## 🔗 TinyURL Integration

All links can optionally be shortened using **TinyURL** via `pyshorteners`.

```python
import pyshorteners

shortener = pyshorteners.Shortener()
short_url = shortener.tinyurl.short(original_url)
```

---

## ☁️ Cloudflare Worker Setup

Expose your encrypted links securely via a Cloudflare Worker. Example endpoint:

```
https://autumn-truth-1dd3.genuinetvlive.workers.dev/?key=<encrypted_value>
```

You can add automatic redirection in the Worker to your actual download backend or proxy server.

---

## 🔄 Mirror Rotation Logic

```python
BASE_URLS = [
    "https://pronoobdrive.onrender.com",
    "https://pronoobdrive-mirror1.onrender.com",
    ...
]
```

Rotates through active mirrors using round-robin or random selection to reduce load and avoid downtime.

---

## 📎 Sample Response

```json
{
  "data": {
    "data": [
      {
        "links": [
          {
            "size": "1.39 GB",
            "url": "https://tinyurl.com/2a6f4dla"
          }
        ],
        "title": "Rings 2017 1080P Brrip X264 Rc Mkv"
      },
      {
        "links": [
          {
            "size": "1.19 GB",
            "url": "https://tinyurl.com/28vaxodp"
          }
        ],
        "title": "Rings 2017 Bluray Hindi English Mkv"
      }
    ],
    "mirror_used": "https://pronoobdrive.onrender.com"
  }
}
```


```

## 📄 License

MIT License — free to use and modify.



