# data.py reads resource data and supplies it as needed

import json, os, random

extensions = (
    {}
)  # we will use custom file extensions (undercover json files) - find them below
# we use the following file structure:
# root/
#   resources/
#     covers/
#       <image files (.jpg, .jpeg, .png, .gif, .svg, .webp)>
#     details/
#       <song comparator song/track details files (.scd, .scsd, .sctd)>
extensions["details"] = [".scd", ".scsd", ".sctd"]
#     playlists/
#       <song comparator playlist files (.scpl, .scp)>
extensions["playlists"] = [".scp", ".scpl"]
#     tracks/
#       <audio/video files (.mp3, .mp4, .m4a, .ogg, .wav)>

# note: reading non-custom file extensions is not done by this file.
#       Updates to the compatibility of this program with more file types may not update this file immediately.
#       For an up-to-date list of supported file types, see the documentation, or refer to visuals.py.


def randomPlaylist() -> str:
    """
    Returns the name of a random song comparator playlist file.

    Returns
    -------
    str
        The name of a random song comparator playlist file.
    """
    playlistfolder = "resources/playlists/"
    playlistfiles = os.listdir(playlistfolder)
    playlistfiles = [f for f in playlistfiles if any(f.endswith(extension) for extension in extensions["playlists"])]
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
    playlistfolder = "resources/playlists/"
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
            with open(playlistfile, "r", encoding="utf-8") as f:
                tracks = json.load(f)
    return tracks


def readTrackDetails(filename: str) -> dict:
    """
    Reads a song comparator song/track details file and returns the details
    of the track.

    Parameters
    ----------
    filename : str
        The name of the file to read. Assumed to NOT include an extension.

    Returns
    -------
    dict
        A dictionary containing the details of the song. May be empty if no song details file is found.
    """
    detailsfolder = "resources/details/"
    details = {}
    for extension in extensions["details"]:
        detailsfile = detailsfolder + filename + extension
        if os.path.exists(detailsfile):
            with open(detailsfile, "r", encoding="utf-8") as f:
                details = json.load(f)
            break
    return details


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


def trackSource(track: dict, trackFolder: str = "resources/tracks/") -> tuple[str, bool, bool]:
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
