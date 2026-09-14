import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import yt_dlp

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YouTube Downloader")
        self.geometry("500x420")
        self.resizable(False, False)

        # State
        self.is_downloading = False
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads", "YouTube")
        os.makedirs(self.download_path, exist_ok=True)

        # Layout
        self.create_widgets()

    def create_widgets(self):
        # URL
        ctk.CTkLabel(self, text="YouTube URL").pack(pady=(20, 5))
        self.url_entry = ctk.CTkEntry(self, width=420, placeholder_text="https://www.youtube.com/watch?v=...")
        self.url_entry.pack(pady=5)

        # Format selector
        ctk.CTkLabel(self, text="Format").pack(pady=(15, 5))
        self.format_var = ctk.StringVar(value="best_video")
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.pack(pady=5)

        ctk.CTkRadioButton(
            format_frame, text="Best video (MP4)",
            variable=self.format_var, value="best_video"
        ).grid(row=0, column=0, padx=10)

        ctk.CTkRadioButton(
            format_frame, text="1080p video",
            variable=self.format_var, value="1080p"
        ).grid(row=0, column=1, padx=10)

        ctk.CTkRadioButton(
            format_frame, text="Audio only (MP3)",
            variable=self.format_var, value="audio"
        ).grid(row=0, column=2, padx=10)

        # Folder
        ctk.CTkLabel(self, text="Download folder").pack(pady=(15, 5))
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(pady=5)

        self.folder_label = ctk.CTkLabel(folder_frame, text=self.download_path, width=320, anchor="w")
        self.folder_label.grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            folder_frame, text="Browse…", width=80,
            command=self.browse_folder
        ).grid(row=0, column=1, padx=5)

        # Download button
        self.download_btn = ctk.CTkButton(
            self, text="Download", width=120,
            command=self.start_download_thread
        )
        self.download_btn.pack(pady=20)

        # Progress
        self.progress = ctk.CTkProgressBar(self, width=420)
        self.progress.set(0)
        self.progress.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Ready", anchor="w")
        self.status_label.pack(pady=(0, 10))

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.folder_label.configure(text=self.download_path)

    def start_download_thread(self):
        if self.is_downloading:
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return

        self.is_downloading = True
        self.download_btn.configure(state="disabled")
        self.progress.set(0)
        self.status_label.configure(text="Starting download…")

        thread = threading.Thread(target=self.run_download, args=(url,), daemon=True)
        thread.start()

    def run_download(self, url):
        fmt = self.format_var.get()

        if fmt == "best_video":
            format_spec = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            postprocessors = []
        elif fmt == "1080p":
            format_spec = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best[height<=1080]"
            postprocessors = []
        elif fmt == "audio":
            format_spec = "bestaudio/best"
            postprocessors = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            format_spec = "best"
            postprocessors = []

        def progress_hook(d):
            if d["status"] == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                downloaded = d.get("downloaded_bytes", 0)
                if total:
                    percent = downloaded / total
                    self.progress.set(percent)
                    speed = d.get("speed_str", "?")
                    eta = d.get("eta_str", "?")
                    self.status_label.configure(text=f"Downloading… {percent*100:.1f}% • {speed} • ETA {eta}")
                else:
                    self.status_label.configure(text="Downloading…")
            elif d["status"] == "finished":
                self.status_label.configure(text="Download finished, processing…")
                self.progress.set(1)

        ydl_opts = {
            "format": format_spec,
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "progress_hooks": [progress_hook],
            "postprocessors": postprocessors,
            "extractor_args": {"youtube": {"player_client": ["web", "web_embedded", "mweb"]}},
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.configure(text="✅ Done!")
            messagebox.showinfo("Success", "Download completed!")
        except Exception as e:
            self.status_label.configure(text="❌ Error")
            messagebox.showerror("Error", f"Download failed:\n{e}")
        finally:
            self.is_downloading = False
            self.download_btn.configure(state="normal")

if __name__ == "__main__":
    app = YouTubeDownloaderApp()
    app.mainloop()