def check_missing_mp3_files():
    """
    Compare songs in the mp3 folder vs Spotify liked songs and report missing files.
    """
    playlist_path = "Spotify_Liked_Songs_List.txt"
    if not os.path.exists(playlist_path):
        print(f"[ERROR] Playlist log file not found: {playlist_path}")
        return []
    with open(playlist_path, "r", encoding="utf-8") as f:
        liked_songs = [line.strip() for line in f if line.strip()]
    mp3_files = [f for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")]
    mp3_files_set = set([sanitize_filename(f.replace(".mp3", "")) for f in mp3_files])
    missing = []
    for song in liked_songs:
        expected_filename = sanitize_filename(song)
        if expected_filename not in mp3_files_set:
            missing.append(song)
    print(f"[RESULT] {len(missing)} songs missing from mp3 folder:")
    for song in missing:
        print(f"  - {song}")
    # Write missing songs to main folder
    missing_path = "Missing_Songs.txt"
    with open(missing_path, "w", encoding="utf-8") as f:
        for song in missing:
            f.write(song + "\n")
    print(f"[LOG] Missing songs list written to {missing_path}")
    return missing
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
), requests_timeout=30)  # Increase timeout to 30 seconds

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
    import time
    import requests
    print("[LOG] Fetching all liked songs from Spotify...")
    all_items = []
    offset = 0
    limit = 50
    max_retries = 5
    while True:
        for attempt in range(max_retries):
            try:
                results = sp.current_user_saved_tracks(limit=limit, offset=offset)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, Exception) as e:
                print(f"[ERROR] Spotify API error on offset {offset}, attempt {attempt+1}/{max_retries}: {e}")
                time.sleep(2 * (attempt + 1))  # Exponential backoff
        else:
            print(f"[ERROR] Failed to fetch songs from Spotify after {max_retries} attempts. Exiting.")
            break
        items = results['items']
        all_items.extend(items)
        print(f"[LOG] Fetched {len(items)} songs (offset {offset})")
        if len(items) < limit:
            break
        offset += limit
        time.sleep(1)  # Delay between requests to avoid rate limiting
    print(f"[LOG] Total liked songs fetched: {len(all_items)}")
    return all_items

def sync_spotify_liked_songs():
    items = get_all_liked_songs(sp)
    spotify_songs = []
    liked_songs_log = []
    for item in items:
        track = item['track']
        track_name = track['name']
        artist = track['artists'][0]['name']
        mp3_filename = f"{track_name} - {artist}.mp3"
        sanitized_name = sanitize_filename(mp3_filename)
        spotify_songs.append(sanitized_name)
        liked_songs_log.append(f"{track_name} - {artist}")
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

    # Write playlist file to main folder
    playlist_path = "Spotify_Liked_Songs.m3u"
    print(f"[LOG] Preparing to write playlist to {os.path.abspath(playlist_path)}")
    print(f"[LOG] Number of songs in playlist: {len(spotify_songs)}")
    write_m3u_playlist(spotify_songs, playlist_path)
    print(f"[LOG] Playlist written to {os.path.abspath(playlist_path)}")

    # Write liked songs log file to main folder
    log_path = "Spotify_Liked_Songs_List.txt"
    with open(log_path, "w", encoding="utf-8") as log_file:
        for entry in liked_songs_log:
            log_file.write(entry + "\n")
    print(f"[LOG] Spotify liked songs list written to {os.path.abspath(log_path)}")
def write_m3u_playlist(mp3_filenames, out_path):
    """
    Write an M3U playlist with #EXTM3U header and #EXTINF lines.
    """
    with open(out_path, "w", encoding="utf-8") as m3u:
        m3u.write("#EXTM3U\n")
        for mp3 in mp3_filenames:
            display_title = mp3.replace(".mp3", "")
            m3u.write(f"#EXTINF:-1,{display_title}\n")
            m3u.write(f"{mp3}\n")

def main():
    parser = argparse.ArgumentParser(description='Sync Spotify liked songs with local library and iPod')
    parser.add_argument('-d', '--download', action='store_true', help='Download missing or new songs from Spotify liked songs')
    parser.add_argument('-m', '--missing', action='store_true', help='Check for missing songs in mp3 folder vs playlist')
    parser.add_argument('-p', '--playlist', action='store_true', help='Regenerate the .m3u playlist and log file')
    args = parser.parse_args()

    if args.download:
        print("[LOG] Checking for missing songs in mp3 folder vs playlist...")
        missing_songs = check_missing_mp3_files()
        if not missing_songs:
            print("[LOG] No missing songs to download.")
        else:
            print(f"[LOG] Downloading {len(missing_songs)} missing songs...")
            for song in missing_songs:
                # Split song into track_name and artist
                if ' - ' in song:
                    track_name, artist = song.split(' - ', 1)
                else:
                    track_name = song
                    artist = ''
                if download_mp3(track_name, artist, MUSIC_DIR):
                    print(f"[LOG] Downloaded: {song}")
                else:
                    print(f"[ERROR] Failed to download: {song}")
            # Delete Missing_Songs.txt after download
            missing_path = "Missing_Songs.txt"
            if os.path.exists(missing_path):
                os.remove(missing_path)
                print(f"[LOG] Deleted {missing_path}")
    elif args.missing:
        print("[LOG] Checking for missing songs in mp3 folder vs playlist...")
        check_missing_mp3_files()
    elif args.playlist:
        print("[LOG] Regenerating playlist and log file...")
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