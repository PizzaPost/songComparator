import json
import os
import data


def calculateStats():
    with open(os.path.join(data.datafolder, "default.json")) as f:
        default = json.load(f)
        f.close()
    daysUsed = len(default.get("dates_used"))
    session_lengths = default.get("session_lengths")
    timeTotal = sum(session_lengths)
    sessionCount = len(session_lengths)
    longestSessionLength = max(session_lengths)
    averageSessionLength = timeTotal / sessionCount
    
    trackRatings = [scv for scv in os.listdir(data.datafolder) if scv.endswith(".scv")]
    ratings = []
    best = []
    worst = []
    artistStars = {}
    replays = 0
    listeningTimes = []
    trackLengths = []
    votingTimes = []
    for rateFile in trackRatings:
        with open(os.path.join(data.datafolder, rateFile), "r", encoding="utf-8") as f:
            trackRating = json.load(f)
            f.close()
        trackData = trackRating.get("trackData")
        replays += trackRating.get("replays")
        listeningTimes.append(trackRating.get("timeListening"))
        trackLengths.append(trackRating.get("trackLength"))
        votingTimes.append(trackRating.get("timeVoting"))
        for index, rating in enumerate(trackRating.get("ratings")):
            ratings.append(rating)
            artist = trackData.get("artist")
            if trackData.get("artist") not in artistStars:
                artistStars[artist] = [0, 0, 0, 0]
            artistStars[artist][index] += rating
            saveTuple = (rating, data.displayName(trackData))
            if len(best) <= index:
                best.append(saveTuple)
            elif best[index][0] < rating:
                best[index] = saveTuple
            if len(worst) <= index:
                worst.append(saveTuple)
            elif worst[index][0] > rating:
                worst[index] = saveTuple
    
    averageRating = sum(ratings) / len(ratings)
    averageRelatability = sum(ratings[::4]) / len(ratings[::4])
    averageLyricsQuality = sum(ratings[1::4]) / len(ratings[1::4])
    averageBeatQuality = sum(ratings[2::4]) / len(ratings[2::4])
    averageBeatTaste = sum(ratings[3::4]) / len(ratings[3::4])
    
    mostRelatable = best[0][1]
    bestLyrics = best[1][1]
    bestBeat = best[2][1]
    tastiest = best[3][1]
    
    leastRelatable = worst[0][1]
    worstLyrics = worst[1][1]
    worstBeat = worst[2][1]
    mostDisgusting = worst[3][1]
    
    mostStarredArtists = sorted(artistStars.items(), key=lambda x: sum(x[1]), reverse=True)[0][0]
    mostRelatableArtists = sorted(artistStars.items(), key=lambda x: x[1][0], reverse=True)[0][0]
    bestLyricsArtists = sorted(artistStars.items(), key=lambda x: x[1][1], reverse=True)[0][0]
    bestProducedArtists = sorted(artistStars.items(), key=lambda x: x[1][2], reverse=True)[0][0]
    tastiestArtist = sorted(artistStars.items(), key=lambda x: x[1][3], reverse=True)[0][0]
    
    mostCommonRating = sorted(set(ratings), key=ratings.count, reverse=True)[0]
    
    tracksRated = len(trackRatings)
    fiveStars = sum(1 for rating in ratings if rating == 5)
    fourStars = sum(1 for rating in ratings if rating == 4)
    threeStars = sum(1 for rating in ratings if rating == 3)
    twoStars = sum(1 for rating in ratings if rating == 2)
    oneStar = sum(1 for rating in ratings if rating == 1)
    
    timeVoting = sum(votingTimes)
    timeListening = sum(listeningTimes)
    averageTimeListened = timeListening / len(listeningTimes)
    averageTimeVoting = timeVoting / len(votingTimes)
    averageTrackLength = sum(trackLengths) / len(trackLengths) / 1000 # trackLength is in ms, convert to s
    
    return {
        "sessionCount": sessionCount,
        "daysUsed": daysUsed,
        "timeTotal": timeTotal,
        "longestSessionLength": longestSessionLength,
        "averageSessionLength": averageSessionLength,
        "averageRating": averageRating,
        "averageRelatability": averageRelatability,
        "averageLyricsQuality": averageLyricsQuality,
        "averageBeatQuality": averageBeatQuality,
        "averageBeatTaste": averageBeatTaste,
        "mostRelatable": mostRelatable,
        "bestLyrics": bestLyrics,
        "bestBeat": bestBeat,
        "tastiest": tastiest,
        "leastRelatable": leastRelatable,
        "worstLyrics": worstLyrics,
        "worstBeat": worstBeat,
        "mostDisgusting": mostDisgusting,
        "mostStarredArtists": mostStarredArtists,
        "mostRelatableArtists": mostRelatableArtists,
        "bestLyricsArtists": bestLyricsArtists,
        "bestProducedArtists": bestProducedArtists,
        "tastiestArtist": tastiestArtist,
        "mostCommonRating": mostCommonRating,
        "tracksRated": tracksRated,
        "fiveStars": fiveStars,
        "fourStars": fourStars,
        "threeStars": threeStars,
        "twoStars": twoStars,
        "oneStar": oneStar,
        "replays": replays,
        "timeVoting": timeVoting,
        "timeListening": timeListening,
        "averageTimeListened": averageTimeListened,
        "averageTrackLength": averageTrackLength,
        "averageTimeVoting": averageTimeVoting
    }

if __name__ == "__main__":
    from pprint import pprint
    pprint(calculateStats(), sort_dicts=False, indent=4)
