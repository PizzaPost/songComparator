# data.py reads resource data and supplies it as needed

import json
import os
import random

import mutagen

extensions = {}
# we will use custom file extensions (undercover json files) - find them below
# we use the following file structure:
# root/
#   resources/
#     covers/
#       <image files (.jpg, .jpeg, .png, .gif, .svg, .webp)>
coverfolder = "resources/covers/"
#     data/
datafolder = "resources/data/"
#     details/
detailsfolder = "resources/details/"
#       <song comparator song/track details files (.scd, .scsd, .sctd)>
extensions["details"] = [".scd", ".scsd", ".sctd"]
#     playlists/
playlistfolder = "resources/playlists/"
#       <song comparator playlist files (.scpl, .scp)>
extensions["playlists"] = [".scp", ".scpl"]
#     tracks/
#       <audio/video files (.mp3, .mp4, .m4a, .ogg, .wav)>
trackfolder = "resources/tracks/"


def randomPlaylist() -> str:
    """
    Returns the name of a random song comparator playlist file.

    Returns
    -------
    str
        The name of a random song comparator playlist file.
    """
    playlistfiles = os.listdir(playlistfolder)
    playlistfiles = [
        f
        for f in playlistfiles
        if any(f.endswith(extension) for extension in extensions["playlists"])
    ]
    return random.choice(playlistfiles)


def readPlaylist(filename: str) -> list:
    """
    Finds a song comparator playlist file and returns the tracks
    in the playlist.

    Parameters
    ----------
    filename : str
        The name of the file to read. Extension optional.

    Returns
    -------
    list
        A list of tracks in the first found corresponding playlist file along with their details. May be empty if no playlist file with the given name is found.
    """
    tracks = []
    found = False
    for extension in extensions["playlists"]:
        playlistfile = playlistfolder + filename + extension
        if os.path.exists(playlistfile):
            with open(playlistfile, "r") as f:
                tracks = json.load(f)
                found = True
            break
    if not found:
        playlistfile = playlistfolder + filename
        if os.path.exists(playlistfile):
            tracks = readJSON(playlistfile)
    return tracks


def details(filename: str, searchContents: bool = False, searchPlaylists: bool = False) -> dict:
    """
    Reads a song comparator song/track details file and returns the details
    of the track.

    Parameters
    ----------
    filename : str
        The name of the track to find the details for. Providing either "track.mp4" or "track" is sufficient.
    searchContents : bool, optional
        Whether to also search the contents of arbitrary details files until the requested track is found as the target track. (Needs extension, i.e. "track.mp4", to be provided)
    searchPlaylists : bool, optional
        Whether to also search the contents of arbitrary playlist files until the requested track is found as a target track. (Needs extension, i.e. "track.mp4", to be provided)
    
    Returns
    -------
    dict
        A dictionary containing the details of the song. May be empty if no song details file is found based on your criteria.
    """
    details = {}
    for _filename in (filename, removeExtension(filename)):
        if _filename == "":
            continue
        for extension in extensions["details"]:
            detailsfile = detailsfolder + _filename + extension
            if os.path.exists(detailsfile):
                details = readJSON(detailsfile)
                return details
    if searchContents:
        for detail in os.listdir(detailsfolder):
            d = readJSON(detailsfolder + detail)
            if d["track"] == filename:
                details = d
    if searchPlaylists:
        for playlist in os.listdir(playlistfolder):
            for track in readPlaylist(playlist):
                if track["track"] == filename:
                    details = track
    return details


def readJSON(file: str):
    with openFile(file) as f:
        j = json.load(f)
    return j


def openFile(file):
    return open(file, "r", encoding="utf-8")


def randomTrack(playlist: list) -> dict:
    """
    Returns a random track from a playlist.

    Parameters
    ----------
    playlist : list
        A list of tracks in a playlist.

    Returns
    -------
    dict
        A random track from the playlist.
    """
    return random.choice(playlist)


def tracks(playlist: list):
    """generator to return one track after the other upon next(tracks)

    Args:
        playlist (list): the playlist data

    Yields:
        dict: track data
    """
    yield from playlist


def trackSource(track: dict, trackFolder: str = trackfolder) -> tuple[str, bool, bool]:
    """
    Returns the source of a track, whether it is a stream (true) or a local file (false), and whether it contains video data.

    Parameters
    ----------
    track : dict
        A track data dictionary.

    Returns
    -------
    source : str
        The source of the track. (url or path into the track folder)
    stream : bool
        Whether the track is a stream (true) or a local file (false).
    audio : bool
        Whether the track is an audio file (true) or a video file (false).
    """
    source = track.get("track") or track.get("url")
    if source is None:
        raise KeyError("Track dictionary does not contain 'track' or 'url' key")
    stream = source == track.get("url")
    isVideo = track.get("type") == 1
    source = trackFolder + source
    return source, stream, isVideo


def removeExtension(text: str):
    for char in text[::-1]:
        text = text[:-1]
        if char == ".":
            break
    return text


def displayName(track: dict):
    artist = track.get("artist")
    title = track.get("title")
    return ((artist + " - ") if artist else "") + (title if title else "")


def save_voting(ratings: list, trackData, total_seconds, replays):
    """Saves the votings in every category for the last played track."""
    print(trackData, replays)


def get_track_length(track):
    """Returns the length of a track in milliseconds.

    Parameters
    ----------
    track : str
        A track name in resources/tracks.

    Returns
    -------
    length : int
        The length of a track in milliseconds.

    Fallback
    -------
        0: int
    """
    audio = mutagen.File(f"{trackfolder}{track}")
    if audio is not None:
        return int(audio.info.length * 1000)  # convert to milliseconds
    return 0  # fallback


def listTrackFolder():
    return os.listdir(trackfolder)


def listPlaylistFolder():
    return os.listdir(playlistfolder)


def load_data(filename: str = "default"):
    if os.path.exists(f"{datafolder}{filename}.json"):
        with open(f"{datafolder}{filename}.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
        return data
    else:
        with open(f"{datafolder}{filename}.json", "w") as f:
            json.dump({}, f, indent=4)
            f.close()
        return {}


def set_value(key: str, value, filename: str = "default"):
    data = load_data(filename)
    data[key] = value
    with open(f"{datafolder}{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.close()


def get_value(key: str, filename: str = "default"):
    data = load_data(filename)
    return data.get(key)


def add_value(key: str, amount: int, filename: str = "default"):
    data = load_data(filename)
    data[key] = data.get(key, 0) + amount
    with open(f"{datafolder}{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.close()


def change_bool(key: str, filename: str = "default"):
    data = load_data(filename)
    data[key] = not data.get(key)
    with open(f"{datafolder}{filename}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.close()
