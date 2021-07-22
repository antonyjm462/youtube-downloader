# Import Required Modules
from tkinter import *
from pyyoutube import Api
from pytube import YouTube
from threading import Thread
from tkinter import messagebox
import re
import os
import pickle

dir_path = os.path.dirname(os.path.realpath(__file__))
dbfile = open('db', 'ab')
dbfile_r = open('db', 'rb')
db = pickle.load(dbfile_r)
for keys in db.keys():
    print(keys, '=>', db[keys])
dbfile_r.close()

def name(video_name, index):
    patten = r'\w+'
    match = re.findall(patten, video_name)
    return f'{index}_{" ".join(match)}'


def get_video():
    # Create API Object
    api = Api(api_key='AIzaSyDUiI60pekLl8Ano_DGrjcUjfWwmRgxH9w')
    

    if "youtube" in videoId.get():
        video_id = videoId.get()[len(
            "https://www.youtube.com/watch?v="):]
    else:
        video_id = videoId.get()
        
    if video_id == "":
        video_id = db['video_id']
        
    db['video_id'] = video_id
    pickle.dump(db, dbfile)

    URL = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(URL)
    stream = yt.streams.filter(
        progressive=True, file_extension='mp4', resolution=videoResolution.get())[0]

    if "home" in location.get():
        download_path = location.get()
    else:
        download_path = f"{dir_path}/{location.get()}"
        
    if download_path == f"{dir_path}/":
        download_path = db['download_path']
        
    db['download_path'] = download_path
    pickle.dump(db, dbfile)

    try:
        stream.download(output_path=download_path)
    except:
        print("Stream Error!")
        messagebox.showinfo("Failed", "Video download failed")
    else:
        messagebox.showinfo("Success", f"Video Successfully downloaded")


def get_list_videos():
    global playlist_item_by_id
    # Clear ListBox
    list_box.delete(0, 'end')

    # Create API Object
    api = Api(api_key='AIzaSyDUiI60pekLl8Ano_DGrjcUjfWwmRgxH9w')

    if "youtube" in playlistId.get():
        playlist_id = playlistId.get()[len(
            "https://www.youtube.com/playlist?list="):]
    else:
        playlist_id = playlistId.get()
        
    if playlist_id == "":
        playlist_id = db['playlist_id']
        
    db['playlist_id'] = playlist_id
    pickle.dump(db, dbfile)
    
    if "home" in location.get():
        download_path = location.get()
    else:
        download_path = f"{dir_path}/{location.get()}"
        
    if download_path == f"{dir_path}/":
        download_path = db['download_path']
        
    db['download_path'] = download_path
    pickle.dump(db, dbfile)

    # Get list of video links
    playlist_item_by_id = api.get_playlist_items(
        playlist_id=playlist_id, count=None, return_json=True)

    # Iterate through all video links and insert into listbox
    for index, videoid in enumerate(playlist_item_by_id['items']):
        list_box.insert(
            END, f" {str(index+1)}. {name(videoid['snippet']['title'], index)}")

    download_start.config(state=NORMAL)


def threading():
    # Call download_videos function
    t1 = Thread(target=download_videos)
    t1.start()


def download_videos():
    download_start.config(state="disabled")
    get_videos.config(state="disabled")

    if "home" in location.get():
        download_path = location.get()
    else:
        download_path = f"{dir_path}/{location.get()}"
        
    if download_path == f"{dir_path}/":
        download_path = db['download_path']
        
    db['download_path'] = download_path
    pickle.dump(db, dbfile)
    
    # Iterate through all selected videos
    for index, videoid in enumerate(playlist_item_by_id['items']):
        link = f"https://www.youtube.com/watch?v={videoid['contentDetails']['videoId']}"

        download_name = name(videoid['snippet']['title'],index)

        print(f"Name: {videoid['snippet']['title']}\nId: {videoid['contentDetails']['videoId']}\nDownloaded Name: {download_name}\nStatus:", end="")

        yt_obj = YouTube(link)

        filters = yt_obj.streams.filter(progressive=True, file_extension='mp4')

        # download the highest quality video
        stream = filters.get_highest_resolution()

        try:
            stream.download(output_path=download_path, filename=download_name,timeout=10)
            print("Sucess")
        except:
            try:
                stream = yt_obj.streams.filter(progressive=True, file_extension='mp4', resolution='720p')[0]
                stream.download(output_path=download_path, filename=download_name)
                print("Sucess")
            except:
                print("-"*100)
                print("Error")
                print(f"Name: {download_name}\nId: {videoid['contentDetails']['videoId']}")
                print("-"*100)
            
    messagebox.showinfo("Success", "Video Successfully downloaded")
    download_start.config(state="normal")
    get_videos.config(state="normal")


# Create Object
root = Tk()
# Set geometry
root.geometry('400x700')

# Playlist Downloder
# Add Label
Label(root, text="Youtube Downloader",
      font="italic 15 bold").pack(pady=10)

# Video Downloder
# Add Label
Label(root, text="Enter Download Location:-", font="italic 10").pack()

# Add Entry box
location = Entry(root, width=60)
location.pack(pady=5)

Label(root, text="Enter Playlist URL:-", font="italic 10").pack()

# Add Entry box
playlistId = Entry(root, width=60)
playlistId.pack(pady=5)

# Add Button
get_videos = Button(root, text="Get Videos", command=get_list_videos)
get_videos.pack(pady=10)

# Video Downloder
# Add Label
Label(root, text="Enter Video URL:-", font="italic 10").pack()

# Add Entry box
videoId = Entry(root, width=60)
videoId.pack(pady=5)

# Add Label
Label(root, text="Enter Video Resolution:-", font="italic 10").pack()

# Add Entry box
videoResolution = Entry(root, width=60)
videoResolution.pack(pady=5)

# Add Button
get_videos = Button(root, text="Get Video", command=get_video)
get_videos.pack(pady=10)


# Add Scollbar
scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=BOTH)
list_box = Listbox(root, selectmode="multiple")
list_box.pack(expand=YES, fill="both")
list_box.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=list_box.yview)

download_start = Button(root, text="Download Start",
                        command=threading, state=DISABLED)
download_start.pack(pady=10)

# Execute Tkinter
root.mainloop()
