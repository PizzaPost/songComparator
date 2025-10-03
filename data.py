# data.py reads resource data and supplies it as needed

import json, os

extensions = {}  # we will use custom file extensions - find them below
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


def findPlaylist(filename: str) -> list:
    """
    Finds a song comparator playlist file and returns the tracks
    in the playlist.

    Parameters
    ----------
    filename : str
        The name of the file to read. Assumed to NOT include an extension.

    Returns
    -------
    list
        A list of tracks in the first found corresponding playlist file along with their details. May be empty if no playlist file with the given name is found.
    """
    playlistfolder = "resources/playlists/"
    tracks = []
    for extension in extensions["playlists"]:
        playlistfile = playlistfolder + filename + extension
        if os.path.exists(playlistfile):
            with open(playlistfile, "r") as f:
                tracks = json.load(f)
            break
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
            with open(detailsfile, "r") as f:
                details = json.load(f)
            break
    return details
