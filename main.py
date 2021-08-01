import streamlit as st
import urllib.request,urllib.error
import youtube_dl
import os,io
import base64
import shutil
import subprocess
import sys
import uuid
import time
import requests
from PIL import Image
import pathlib
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    st.error("このサイトはYoutubeの動画をダウンロードするサイトです")
    st.error("※ 違法なダウンロードは絶対にしないでください ※")
    st.error("※ Never download illegally ※")
    st.error("※ 必ず自己責任で使用してください ※")
    st.error("※ Please be sure to use at your own risk ※")
    try:
        dirid = str(uuid.uuid4())
        outpath = os.path.join(tmpdir,f"{dirid}.mp4")
        audiopath = os.path.join(tmpdir,f"{dirid}.mp3")
        try:
            shutil.rmtree(os.path.dirname(outpath))
        except:
            pass
        try:
            os.makedirs(os.path.dirname(outpath))
        except:
            pass
        try:
            os.remove(outpath)
        except:
            pass
    except:
        pass

    def checkURL(url):
        try:
            check = urllib.request.urlopen(url)
            check.close()
            return True
        except:
            return False

    def getsamnail(url):
        ydl = youtube_dl.YoutubeDL({})
        with ydl:
            result = ydl.extract_info(
                url,
                download=False # We just want to extract the info
            )

        checklist = []
        for data in result["thumbnails"]:
            checklist.append(data["height"])
            maxdata = max(checklist)

        dlurl = ""
        for data in result["thumbnails"]:
            if data["height"] == maxdata:
                dlurl = data["url"]
        return dlurl

    dlset = False
    urlinput = st.text_input(label="Please enter the URL of Youtube")
    img = st.empty()

    if urlinput is not None:
        if checkURL(urlinput):
            if not dlset:
                for num in range(3):
                    try:
                        movielist = []
                        idjson = {'max_filesize':873741824}
                        ydl_opts = {'format': 'bestaudio/best'}
                        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                            meta = ydl.extract_info(
                                urlinput, download=False) 
                            formats = meta.get('formats', [meta]) 
                        videoimg = Image.open(io.BytesIO(requests.get(getsamnail(urlinput)).content))
                        wsize = 800
                        hsize = 500
                        w, h = videoimg.size
                        if wsize < w:
                            videoimg = videoimg.resize((wsize,hsize))
                        elif hsize < h:
                            videoimg = videoimg.resize((wsize,hsize))
                        else:
                            videoimg = videoimg.copy()
                        img.image(videoimg, caption='thumbnail')
                        for format in formats:
                            bitrate = format["asr"]
                            format_id = format["format_id"]
                            format_note = format["format_note"]
                            format_width = format["width"]
                            format_height = format["height"]
                            format_ext = format["ext"]
                            format_fps = format["fps"]
                            dlurl = format["url"]
                            movielist.append(f"image quality {format_note}\t{format_fps}fps\tformat {format_ext}")
                            idjson.setdefault(f"image quality {format_note}\t{format_fps}fps\tformat {format_ext}",format_id)
                        dloption = st.selectbox("ダウンロードする画質を選んでください",movielist)
                        break
                    except:
                        import traceback
                        traceback.print_exc()
                        st.error("An error occurred while retrieving video information")
                        continue
        else:
            st.error("URL not found")

    donebtn = st.button("Download Now")
    bar = st.progress(0)

    def getprogress(d):
        global bar
        parsent = int(int(d["downloaded_bytes"])/int(d["total_bytes"])*100)
        bar.progress(parsent)

    if donebtn:
        nowtime = time.time()
        dlset = True
        try:
            st.write("Downloading the video")
            ydl = youtube_dl.YoutubeDL({'outtmpl':outpath,'format':idjson[dloption],'progress_hooks': [getprogress],"quiet":True})
            with ydl:
                result = ydl.extract_info(
                    urlinput,
                    download=True # We just want to extract the info
                )
            st.write("Downloading audio")
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl':  audiopath,
                'progress_hooks': [getprogress],"quiet":True
            }
            ydl = youtube_dl.YoutubeDL(ydl_opts)
            info_dict = ydl.extract_info(urlinput,download=True)
            st.write("Combines video and audio")
            margepath = os.path.join(tmpdir,f"{dirid}.mp4")
            try:
                subprocess.run(f"ffmpeg -i {outpath} -i {audiopath} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {margepath}".split(" "))
            except:
                import traceback
                traceback.print_exc()
            st.video(margepath)
            st.write(f"ダウンロードにかかった時間{int(time.time()-nowtime)}")
            try:
                shutil.rmtree(os.path.dirname(outpath))
            except:
                pass
        except:
            import traceback
            traceback.print_exc()
            st.error("何らかのエラーが発生しました")
            try:
                shutil.rmtree(os.path.dirname(outpath))
            except:
                pass
        dlset = False