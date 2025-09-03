
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from difflib import get_close_matches
import yt_dlp
import argparse
import re

MUSIC_DIR = "mp3"

def sanitize_filename(filename):
    filename = re.sub(r'[\\/:*?"<>|]', '', filename)
    filename = re.sub(r'[^\x00-\x7F]', '', filename)
    return filename

os.makedirs(MUSIC_DIR, exist_ok=True)
local_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="0755dd447deb4514837f7f821c0cbd42",
    client_secret="9cae9ee58ae342d393414625dde6c9f9",
    redirect_uri="http://127.0.0.1:8000/callback",
    scope="user-library-read"
))

def find_match(track_name, artist):
    query = f"{track_name} {artist}".lower()
    print(f"[LOG] Searching for local MP3 match: '{query}'")
    matches = get_close_matches(query, [f.lower() for f in local_files], n=1, cutoff=0.5)
    if matches:
        print(f"[LOG] Found local match: {matches[0]}")
    else:
        print(f"[LOG] No local match found for: {query}")
    return matches[0] if matches else None

def download_mp3(track_name, artist, out_dir):
    search_query = f"ytsearch1:{track_name} {artist} audio"
    print(f"[LOG] Attempting to download MP3 for: {track_name} - {artist}")
    sanitized_name = sanitize_filename(f"{track_name} - {artist}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_dir, f"{sanitized_name}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"[LOG] Downloading from YouTube with query: {search_query}")
            info = ydl.extract_info(search_query, download=True)
            print(f"[LOG] Downloaded: {track_name} - {artist}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to download {track_name} - {artist}: {e}")
            return False

def get_all_liked_songs(sp):
    print("[LOG] Fetching all liked songs from Spotify...")
    all_items = []
    offset = 0
    limit = 50
    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results['items']
        all_items.extend(items)
        print(f"[LOG] Fetched {len(items)} songs (offset {offset})")
        if len(items) < limit:
            break
        offset += limit
    print(f"[LOG] Total liked songs fetched: {len(all_items)}")
    return all_items

def sync_spotify_liked_songs():
    items = get_all_liked_songs(sp)
    spotify_songs = []
    for item in items:
        track = item['track']
        track_name = track['name']
        artist = track['artists'][0]['name']
        mp3_filename = f"{track_name} - {artist}.mp3"
        sanitized_name = sanitize_filename(mp3_filename)
        spotify_songs.append(sanitized_name)
        print(f"[LOG] Processing: {track_name} - {artist}")
        match = find_match(track_name, artist)
        if not match:
            print(f"[LOG] MP3 not found locally. Downloading...")
            if download_mp3(track_name, artist, MUSIC_DIR):
                local_files.append(sanitized_name)
        else:
            print(f"[LOG] MP3 found locally: {match}")
    # Optionally remove local files that are no longer in Spotify liked songs
    for local_file in local_files[:]:
        sanitized_local_file = sanitize_filename(local_file)
        if sanitized_local_file not in spotify_songs:
            print(f"[LOG] Removing {local_file} as it's no longer in Spotify liked songs")
            try:
                os.remove(os.path.join(MUSIC_DIR, local_file))
                local_files.remove(local_file)
            except Exception as e:
                print(f"[ERROR] Failed to remove {local_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Download Spotify liked songs to local mp3 folder')
    parser.add_argument('-d', '--download', action='store_true', help='Download missing or new songs from Spotify liked songs')
    args = parser.parse_args()
    print("[LOG] Running in download mode - syncing Spotify liked songs")
    sync_spotify_liked_songs()

if __name__ == "__main__":
    main()

def download_mp3(track_name, artist, out_dir):
    search_query = f"ytsearch1:{track_name} {artist} audio"
    print(f"[LOG] Attempting to download MP3 for: {track_name} - {artist}")
    sanitized_name = sanitize_filename(f"{track_name} - {artist}")
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(out_dir, f"{sanitized_name}.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'embed-metadata': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"[LOG] Downloading from YouTube with query: {search_query}")
            info = ydl.extract_info(search_query, download=True)
            print(f"[LOG] Downloaded: {track_name} - {artist}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to download {track_name} - {artist}: {e}")
            return False

def get_all_liked_songs(sp):
    print("[LOG] Fetching all liked songs from Spotify...")
    all_items = []
    offset = 0
    limit = 50
    while True:
        results = sp.current_user_saved_tracks(limit=limit, offset=offset)
        items = results['items']
        all_items.extend(items)
        print(f"[LOG] Fetched {len(items)} songs (offset {offset})")
        if len(items) < limit:
            break
        offset += limit
    print(f"[LOG] Total liked songs fetched: {len(all_items)}")
    return all_items

def main():
    parser = argparse.ArgumentParser(description='Sync Spotify liked songs with local library and iPod')
    parser.add_argument('-d', '--download', action='store_true', 
                       help='Download missing or new songs from Spotify liked songs')
    parser.add_argument('--no-itunes', action='store_true',
                       help='Skip iTunes sync process (files will be copied but not visible)')
    args = parser.parse_args()
    
    if args.download:
        print("[LOG] Running in download mode - syncing Spotify liked songs")
        sync_spotify_liked_songs()
    else:
        print("[LOG] Running in normal mode - processing all liked songs")
        items = get_all_liked_songs(sp)
        print(f"[LOG] Found {len(items)} liked songs.")
        for idx, item in enumerate(items, 1):
            track = item['track']
            track_name = track['name']
            artist = track['artists'][0]['name']
            mp3_filename = f"{track_name} - {artist}.mp3"
            sanitized_name = sanitize_filename(mp3_filename)
            print(f"[STEP {idx}] Processing: {track_name} - {artist}")
            match = find_match(track_name, artist)
            if not match:
                print(f"[LOG] MP3 not found locally. Downloading...")
                if download_mp3(track_name, artist, MUSIC_DIR):
                    local_files.append(sanitized_name)
            else:
                print(f"[LOG] MP3 found locally: {match}")
    

if __name__ == "__main__":
    main()