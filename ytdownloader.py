import yt_dlp
import re
import os
from pathlib import Path

def is_valid_youtube_url(url):
    """Validate if the URL is a YouTube URL"""
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
    return re.match(youtube_regex, url) is not None

def get_deno_path():
    """Get the deno executable path, platform-independent"""
    # Try common deno installation locations
    home = str(Path.home())
    possible_paths = [
        Path(home) / ".deno" / "bin" / "deno.exe" if os.name == 'nt' else Path(home) / ".deno" / "bin" / "deno",
        Path("/usr/local/bin/deno"),
        Path("/usr/bin/deno"),
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # If deno not found, return None and let yt_dlp use default
    return None

url = input("Enter YouTube URL: ").strip()

# Validate URL
if not url:
    print("❌ Error: URL cannot be empty")
    exit(1)

if not is_valid_youtube_url(url):
    print("❌ Error: Invalid YouTube URL")
    exit(1)

ydl_opts = {
    "format": "best",
    "outtmpl": "downloads/%(title)s.%(ext)s",
    "extractor_args": {"youtube": {"player_client": ["web", "web_embedded", "mweb"]}},
}

# Only add deno path if it exists
deno_path = get_deno_path()
if deno_path:
    ydl_opts["js_runtimes"] = {"deno": {"path": deno_path}}

try:
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print("\n✅ Done!")
except yt_dlp.utils.DownloadError as e:
    print(f"\n❌ Download Error: {e}")
except yt_dlp.utils.ExtractorError as e:
    print(f"\n❌ Extractor Error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
