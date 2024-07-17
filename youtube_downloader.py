import os
import time
import yt_dlp
import zipfile
from PIL import Image
import streamlit as st


def download_video(url, download_type):
    ydl_opts = {}
    downloaded_files = []

    if download_type == "Video":
        ydl_opts = {"format": "best[height<=1080]", "outtmpl": "%(title)s.%(ext)s"}
    elif download_type == "Audio":
        ydl_opts = {"format": "bestaudio", "outtmpl": "%(title)s.%(ext)s"}
    elif download_type == "Playlist":
        ydl_opts = {
            "yes_playlist": True,
            "format": "bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
        }

    # Initialize Streamlit progress bar and status text
    progress_bar = st.progress(0)
    status_text = st.empty()
    downloaded_bytes = 0
    video_count = 0
    all_video_count = 1

    # Inner function to handle the progress bar
    def progress_hook(d):
        nonlocal downloaded_bytes
        nonlocal video_count, all_video_count
        if d["status"] == "downloading" and download_type != "Playlist":
            downloaded_bytes += d["downloaded_bytes"] - downloaded_bytes
            progress = downloaded_bytes / total_size
            progress_bar.progress(progress)
            status_text.text(f"Downloaded {round(progress*100)}%")
        elif download_type == "Playlist" and d["status"] == "finished":
            video_count += 1
            progress = video_count / all_video_count
            progress_bar.progress(progress)
            status_text.text(f"Downloaded videos {video_count} from {all_video_count}")
            if video_count == all_video_count:
                status_text.text(f"Download Completed")
            downloaded_files.append(d["filename"])
        elif d["status"] == "finished":
            downloaded_files.append(d["filename"])
            progress_bar.progress(1.0)

    ydl_opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        with st.spinner(text=f"Getting {download_type}"):
            info_dict = ydl.extract_info(url, download=False)
        all_video_count = len(info_dict.get("entries", [0]))
        if download_type == "Playlist":
            status_text.text(f"Downloaded {video_count} from {all_video_count}")
        else:
            status_text.text(f"Downloaded 0%")
        total_size = (
            info_dict.get("filesize", 0)
            or info_dict.get("filesize_approx", 0)
            or sum([entry.get("filesize", 0) for entry in info_dict.get("entries", [])])
        )
        ydl.download([url])
    if download_type == "Playlist":
        zip_file_name = info_dict.get("title", "downloaded_zip")
        zip_file_name += ".zip"
        st.write("Zip name:", zip_file_name)
        os.makedirs("Zips", exist_ok=True)
        download_file_name = os.path.join("Zips", zip_file_name)
        with zipfile.ZipFile(download_file_name, "w") as zipf:
            for file in downloaded_files:
                zipf.write(file, file)
                os.remove(file)
    elif download_type == "Audio":
        os.makedirs("Audios", exist_ok=True)
        file = downloaded_files[0]
        st.write("Audio name:", file)
        download_file_name = os.path.join("Audios", file)
        os.rename(file, download_file_name)
    elif download_type == "Video":
        os.makedirs("Videos", exist_ok=True)
        file = downloaded_files[0]
        st.write("Video name:", file)
        download_file_name = os.path.join("Videos", file)
        os.rename(file, download_file_name)
    return download_file_name


# Streamlit app
def main():
    st.title("YouTube Downloader")

    url = st.text_input("Enter YouTube URL")
    download_type = st.selectbox("Select download type", ["Video", "Audio", "Playlist"])
    if st.button(f"Get {download_type}"):
        if ("&list" in url or "?list" in url) and download_type != "Playlist":
            st.write(
                f"Provided Playlist URL, but download_type is set to '{download_type}'. If you want to download entire playlist, please change download_type to 'Playlist'"
            )
        else:
            download_file_name = download_video(url, download_type)
            with open(download_file_name, "rb") as file:
                st.download_button(
                    label=f"Save {download_type} To Computer",
                    data=file,
                    file_name=os.path.basename(download_file_name),
                    mime="application/octet-stream",
                )


if __name__ == "__main__":
    im = Image.open("favicon.ico")
    st.set_page_config(page_title="Youtube Downloader", page_icon=im)
    main()
