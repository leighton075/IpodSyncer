import os
import random

M3U_PATH = os.path.join(os.path.dirname(__file__), "mp3", "Spotify_Liked_Songs.m3u")

def shuffle_m3u(m3u_path):
    if not os.path.exists(m3u_path):
        print(f"[ERROR] Playlist not found: {m3u_path}")
        return

    with open(m3u_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines or not lines[0].startswith("#EXTM3U"):
        print("[ERROR] Not a valid M3U playlist.")
        return

    header = lines[0]
    entries = lines[1:]

    # Group lines into [#EXTINF, filename] pairs
    pairs = []
    i = 0
    while i < len(entries):
        if entries[i].startswith("#EXTINF"):
            if i + 1 < len(entries):
                pairs.append((entries[i], entries[i+1]))
                i += 2
            else:
                break
        else:
            i += 1

    random.shuffle(pairs)

    with open(m3u_path, "w", encoding="utf-8") as f:
        f.write(header)
        for extinf, filename in pairs:
            f.write(extinf)
            f.write(filename)

    print(f"[LOG] Shuffled playlist written to {m3u_path}")

if __name__ == "__main__":
    shuffle_m3u(M3U_PATH)