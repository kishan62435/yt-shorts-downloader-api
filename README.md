## YouTube Shorts Downloader API (FastAPI)

A minimal Python API backend that searches and downloads YouTube Shorts using `yt-dlp`, with JWT-based authentication and static hosting of downloaded files.

### Features
- **FastAPI** server with interactive docs (`/docs`, `/redoc`)
- **JWT auth**: login to obtain a bearer token and access protected endpoints
- **Download Shorts** by keyword search or by channel URL/handle/ID
- **Static hosting** of downloaded files via `/videosList/...`
- **Structured logging** to `logs/` (error, warning, info)
- Centralized **exception handling** with clear HTTP responses
- **No YouTube Data API key** required (uses `yt-dlp`, not the official YouTube Data API)

### No YouTube Data API key
This project does not use the official YouTube Data API. It relies on `yt-dlp` to extract metadata and download content directly from YouTube pages. As a result:
- You do not need to provision or manage a YouTube API key.
- Behavior may change if YouTube updates its site; keeping `yt-dlp` up to date is recommended.

### Repository layout
```text
yt-shorts-downloader-api/
  app/
    api/v1/
      endpoints/
        auth.py        # /auth/login, /auth/logout
        video.py       # /videos/download (protected)
      dependencies/
        auth.py        # get_current_user (JWT header parsing)
    core/
      mainScript.py    # yt-dlp integration and download workflow
      security.py      # JWT create/verify
      hashing.py       # password hashing/verification (bcrypt)
      config.py        # env config for JWT + credentials
      logging_config.py
      exception_handlers.py
    schemas/
      downloadParams.py  # request models (keyword/channel)
      user.py            # user + token models
    main.py             # FastAPI app, CORS, routers, static files
  run.py                # uvicorn entry point (0.0.0.0:8001)
  logs/                 # created at runtime
  videos/               # download output (served at /videosList)
```

### Requirements
- Python 3.10+ (3.11 recommended)
- pip

### Install
```bash
cd yt-shorts-downloader-api
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### Environment variables
Create `yt-shorts-downloader-api/.env` with:
```env
# JWT
SECRET_KEY=replace_with_a_long_random_string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720

# Simple credential check for /auth/login
USERNAME=admin@example.com
PASSWORD=your_password
```

Notes:
- The login endpoint compares your submitted credentials against `USERNAME`/`PASSWORD` from `.env` (hashed at runtime). There is no user database.
- Cookie-based downloads: `app/core/mainScript.py` uses a default `cookies.txt` path (`/home/ubuntu/.yt-dlp/cookies.txt`). If you need cookies to access restricted videos, update `DEFAULT_COOKIES_PATH` in that file to match your OS path (e.g., `C:\Users\<you>\cookies.txt` on Windows).

### Run the API
```bash
cd yt-shorts-downloader-api
python run.py
# Serves on http://0.0.0.0:8001
```

Interactive docs: `http://localhost:8001/docs`

### How downloads are stored and served
- Files are saved under `yt-shorts-downloader-api/videos/`.
- The folder is mounted at the route prefix `/videosList`.
- Example static URL (after a successful download):
  - `http://localhost:8001/videosList/<Channel_or_Base>/<index>_<videoId>_combined.mp4`

### API

#### 1) Login
- **POST** `/auth/login`
- Body:
```json
{
  "email": "admin@example.com",
  "password": "your_password"
}
```
- Response:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Use the `access_token` as `Authorization: Bearer <JWT>` for protected endpoints.

#### 2) Download YouTube Shorts (protected)
- **POST** `/videos/download`
- Accepts one of two bodies:

Keyword search:
```json
{
  "search_type": "keyword",
  "query": "motivational",
  "max_results": 5
}
```

Channel-based search (URL, @handle, or channel ID):
```json
{
  "search_type": "channel",
  "channel_url": "https://www.youtube.com/@SomeChannel",
  "max_results": 5
}
```

Example request (curl):
```bash
curl -X POST "http://localhost:8001/videos/download" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <YOUR_JWT>" \
  -d '{
        "search_type": "keyword",
        "query": "funny cats",
        "max_results": 3
      }'
```

Successful response:
```json
{
  "success": true,
  "message": "Video downloaded successfully",
  "video_urls": [
    "/videosList/<Channel_or_Base>/1_<videoId>_combined.mp4",
    "/videosList/<Channel_or_Base>/2_<videoId>_combined.mp4"
  ]
}
```

Validation & errors:
- `max_results` must be between 1 and 100.
- 401 for invalid/missing token.
- 422 for request validation errors.
- 500 for unhandled exceptions.

### What gets downloaded
This service targets YouTube Shorts specifically:
- Keyword mode issues a `ytsearch... shorts` query.
- Channel mode crawls `<channel>/shorts` only.

### Logging
- Logs are written to `logs/` using rotating file handlers:
  - `logs/error.log`, `logs/warning.log`, `logs/info.log`
- Console logs are also enabled.

### CORS
Default `origins` in `app/main.py` include `http://localhost:3000` and `*` (allow all). Tighten this in production.

### Troubleshooting
- Ensure `yt-dlp` is up-to-date (already pinned in `requirements.txt`).
- If some Shorts require login, place a valid `cookies.txt` and update `DEFAULT_COOKIES_PATH` in `app/core/mainScript.py` for your OS.
- If you run the app from a different working directory, the `videos/` mount path in `app/main.py` uses `os.getcwd()`; run from `yt-shorts-downloader-api/` so static URLs work as documented.
- Because this does not use the official YouTube Data API, occasional breakage can occur due to site changes; update `yt-dlp` and retry.

### Limitations and roadmap
- No persistent user store; single credential pair via env.
- No background job queue; downloads happen in-request.
- Only Shorts are targeted; normal long-form videos are not fetched.
- No rate limiting.

### Legal and disclaimer
- This repository is provided for **educational and research purposes** only.
- The project is **not affiliated with, endorsed by, or sponsored by** YouTube or Google.
- Downloading content may violate **YouTube’s Terms of Service** and/or **copyright laws** depending on your jurisdiction and use case. In general, you should not download content unless you own it, have the copyright holder’s permission, or YouTube explicitly provides a download feature for that content.
- You are solely responsible for how you use this software. The authors and maintainers **do not accept any responsibility or liability** for misuse or any consequences arising from its use.


