import yt_dlp
import streamlit as st
import zipfile
import os
from PIL import Image


im = Image.open("favicon.ico")
st.set_page_config(page_title="Youtube Downloader", page_icon=im)

def download_video(url, download_type):
    ydl_opts = {}
    downloaded_files = []

    if download_type == 'Video':
        ydl_opts = {'format': 'bestvideo[height<=1080]+bestaudio', 
                    'outtmpl': '%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'webm',
                    }],
        }
    elif download_type == 'Audio':
        ydl_opts = {'format': 'bestaudio', 'outtmpl': '%(title)s.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
    elif download_type == 'Playlist':
        ydl_opts = {
            'yes_playlist': True,
            'format': 'bestaudio',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
        }

    # Initialize Streamlit progress bar and status text
    progress_bar = st.progress(0)
    status_text = st.empty()
    downloaded_bytes = 0

    # Inner function to handle the progress bar
    def progress_hook(d):
        nonlocal downloaded_bytes
        if d['status'] == 'downloading':
            downloaded_bytes += d['downloaded_bytes'] - downloaded_bytes
            progress = downloaded_bytes / total_size
            progress_bar.progress(progress)
            status_text.text(f"Convertion {downloaded_bytes} of {total_size} bytes")
        elif d['status'] == 'finished':
            downloaded_files.append(d['filename'])
            progress_bar.progress(1.0)
            status_text.text(f"Convertion Completed")

    ydl_opts['progress_hooks'] = [progress_hook]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        with st.spinner(text=f"Converting {download_type}"):
            info_dict = ydl.extract_info(url, download=False)
        total_size = info_dict.get('filesize', 0) or info_dict.get('filesize_approx', 0) or sum([entry.get('filesize', 0) for entry in info_dict.get('entries', [])])
        ydl.download([url])
    if download_type == "Playlist":
        zip_file_name = info_dict.get("title", "downloaded_zip")
        zip_file_name += '.zip'
        st.write("Zip name:", zip_file_name)
        os.makedirs("Zips", exist_ok=True)
        download_file_name = os.path.join("Zips", zip_file_name)
        with zipfile.ZipFile(download_file_name, 'w') as zipf:
            for file in downloaded_files:
                if download_type == 'Audio' or download_type == 'Playlist':
                    file = file.replace(".webm", ".mp3")
                zipf.write(file, file)
                os.remove(file)
    elif download_type == "Audio":
        os.makedirs("Audios", exist_ok=True)
        file = downloaded_files[0]
        file = file.replace(".webm", ".mp3")
        download_file_name = os.path.join("Audios", file)
        os.rename(file, download_file_name)
    elif download_type == "Video":
        os.makedirs("Videos", exist_ok=True)
        file = downloaded_files[0]
        file = file.split('.webm')[0][:-5] + '.webm'
        download_file_name = os.path.join("Videos", file)
        os.rename(file, download_file_name)
    return download_file_name

# Streamlit app
def main():
    st.title("YouTube Downloader")
    
    url = st.text_input("Enter YouTube URL")
    download_type = st.selectbox("Select download type", ["Video", "Audio", "Playlist"])
    if st.button("Convert"):
        if ("&list" in url or "?list" in url) and download_type != "Playlist":
            st.write(f"Provided Playlist URL, but download_type is set to '{download_type}'. If you want to download entire playlist, please change download_type to 'Playlist'")
        else:
            download_file_name = download_video(url, download_type)
            with open(download_file_name, 'rb') as file:
                st.download_button(
                    label=f"Download {download_type}",
                    data=file,
                    file_name=os.path.basename(download_file_name),
                    mime='application/octet-stream'
                )
if __name__ == "__main__":
    main()
