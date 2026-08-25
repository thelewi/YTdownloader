import yt_dlp

url = input("Enter YouTube URL: ")

ydl_opts = {
    "format": "best",
    "outtmpl": "%(title)s.%(ext)s",
    "js_runtimes": {"deno": {"path": r"C:\Users\user\.deno\bin\deno.EXE"}},
    "extractor_args": {"youtube": {"player_client": ["web", "web_embedded", "mweb"]}},
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print("\n✅ Done!")
except Exception as e:
    print(f"\n❌ Error: {e}")

