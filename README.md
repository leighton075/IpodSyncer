# IpodSyncer

Quick tool to sync Spotify liked songs to local MP3s and generate playlists.
Mainly used in combination with a matcha and feminist literature.

## Setup

Install dependencies:
```bash
pip install spotipy yt-dlp
```

Set up Spotify API credentials in the code (yeah I know, should be env vars).

## Usage

```bash
# Generate playlist and song list from Spotify
py sync.py -p

# Check what songs are missing locally
py sync.py -m

# Download missing songs
py sync.py -d

# Process everything (default)
py sync.py
```

## TODO

### M3U Playlist Improvements
- [ ] Add track duration to `#EXTINF` entries (currently just using -1)
- [ ] Include artist/title parsing for better `#EXTINF` format
- [ ] Add `#PLAYLIST:` header with playlist name
- [ ] Maybe add album info with `#EXTALB:` and `#EXTART:`
- [ ] Consider file size info with `#EXTBYT:`

### General
- [ ] Move Spotify credentials to environment variables
- [ ] Better error handling for network issues
- [ ] Progress bars for downloads
- [ ] Config file for output directories
- [ ] Metadata tagging for downloaded MP3s

## Files

- `mp3/` - Downloaded songs go here
- `Spotify_Liked_Songs.m3u` - Playlist file (in mp3 folder)
- `Spotify_Liked_Songs_List.txt` - Song list for comparison
- `Missing_Songs.txt` - Songs that
