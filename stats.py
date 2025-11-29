import json
import math
import os

import cv2
import pygame

import data
import misc


def calculateStats(playlist=None):
    with open(os.path.join(data.datafolder, "default.json")) as f:
        default = json.load(f)
        f.close()
    daysUsed = len(default.get("dates_used"))
    session_lengths = default.get("session_lengths")
    timeTotal = sum(session_lengths)
    sessionCount = len(session_lengths)
    longestSessionLength = max(session_lengths)
    averageSessionLength = timeTotal / sessionCount
    if playlist:
        playlist = data.readPlaylist(playlist)
        playlist_tracks = []
        for track in playlist:
            playlist_tracks.append(track.get("track") or track.get("url"))
        trackRatings = [scv for scv in os.listdir(data.datafolder) if scv.endswith(".scv") and (
                data.removeExtension(scv) in [data.removeExtension(_track) for _track in
                                              playlist_tracks] or scv in playlist_tracks)]
    else:
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
    tastiestArtists = sorted(artistStars.items(), key=lambda x: x[1][3], reverse=True)[0][0]

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
    averageTrackLength = sum(trackLengths) / len(trackLengths) / 1000  # trackLength is in ms, convert to s

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
        "tastiestArtists": tastiestArtists,
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


width, height = 1080, 1920
fps = 30
animation_base_speed = 6.0
default_slide_duration = 6.0
slide_durations = {
    0: 6.0,
    1: 7.0,
    2: 6.0,
    3: 7.0,
    4: 23.0,
    5: 11.0,
    6: 24.0,
    7: 9.0,
}
transition_duration = 1.0
COLORS = {
    "bg_purple": (140, 100, 255), "bg_green": (100, 255, 100),
    "bg_black": (18, 18, 18), "bg_pink": (255, 100, 180),
    "bg_darkblue": (20, 20, 60), "bg_orange": (255, 140, 50),
    "text_black": (0, 0, 0), "text_white": (255, 255, 255),
    "accent_yellow": (255, 220, 50)
}
lang = misc.load_language(misc.load_settings())


def draw_text_centered(surface, text, font, color, center_x, center_y, alpha=255, return_pos=False):
    text_obj = font.render(text, True, color)
    if alpha < 255:
        text_obj.set_alpha(alpha)
    rect = text_obj.get_rect(center=(center_x, center_y))
    surface.blit(text_obj, rect)
    if return_pos:
        return rect.x, rect.y
    else:
        return None


def ease_out_cubic(current_progress):
    return 1 - pow(1 - current_progress, 3)


def ease_in_out_sin(current_progress):
    return -(math.cos(math.pi * current_progress) - 1) / 2


def get_text_alpha(progress, delay_start=0.1, fade_duration=0.5):
    local_progress = max(0, min(1, (progress - delay_start) / fade_duration))
    ease = ease_out_cubic(local_progress)
    return int(255 * ease)


def format_time(seconds):
    minutes = seconds / 60
    s = int((seconds * 60) % 60)
    m = int(minutes)
    return f"{m}m {s}s"


def draw_horizontal_bar(surface, x, y, w, h, progress, color, bg_color):
    pygame.draw.rect(surface, bg_color, (x, y, w, h), border_radius=h // 2)
    actual_w = w * progress
    if actual_w > 0:
        pygame.draw.rect(surface, color, (x, y, actual_w, h), border_radius=h // 2)


def slide_1_intro(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_purple"]
    surface.fill(bg)
    anim_y = 200 * (1 - ease_out_cubic(min(progress * 2, 1)))
    draw_text_centered(surface, "Wrapped" if not lang else lang["stats"]["title"], fonts["mega"],
                       COLORS["accent_yellow"], width // 2, 250 + anim_y)
    draw_text_centered(surface, playlist, fonts["title"], COLORS["text_black"], width // 2, 450 + anim_y)

    stats_txt = [
        f"{stats["sessionCount"]} Sessions" if not lang else lang["stats"]["sessions"].format(
            str(stats["sessionCount"])),
        f"{stats["daysUsed"]} Days Active" if not lang else lang["stats"]["active_days"].format(str(stats["daysUsed"])),
        f"Total Time: {int(stats["timeTotal"] / 60)} mins" if not lang else lang["stats"]["total_time"].format(
            str(int(stats["timeTotal"] / 60)))
    ]
    start_y = 800
    for i, line in enumerate(stats_txt):
        local_progress = max(0, min(1, (progress - (i * 0.15)) * 2))
        ease = ease_out_cubic(local_progress)
        offset_x = (1 - ease) * -width if i % 2 == 0 else (1 - ease) * width
        if local_progress > 0:
            draw_text_centered(surface, line, fonts["header"], COLORS["text_white"], width // 2 + offset_x,
                               start_y + (i * 180))


def slide_2_sessions(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_darkblue"]
    surface.fill(bg)
    alpha = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Deep Dive Sessions" if not lang else lang["stats"]["title2"], fonts["title"],
                       COLORS["bg_green"], width // 2, 200, alpha=alpha)
    scale1 = ease_out_cubic(min(1, progress * 1.5))
    pygame.draw.circle(surface, COLORS["bg_pink"], (width // 2, 650), 300 * scale1)
    alpha1 = get_text_alpha(progress, delay_start=0.2, fade_duration=0.5)
    if progress > 0.2:
        draw_text_centered(surface, "Longest Session" if not lang else lang["stats"]["longest_session"], fonts["body"],
                           COLORS["text_black"], width // 2, 550,
                           alpha=alpha1)
        draw_text_centered(surface, format_time(stats["longestSessionLength"]), fonts["header_big"],
                           COLORS["text_black"], width // 2, 650, alpha=alpha1)
    scale2 = ease_out_cubic(max(0, min(1, (progress - 0.5) * 1.5)))
    pygame.draw.circle(surface, COLORS["bg_orange"], (width // 2, 1350), 250 * scale2)
    alpha2 = get_text_alpha(progress, delay_start=0.75, fade_duration=0.5)
    if progress > 0.75:
        draw_text_centered(surface, "Average Session" if not lang else lang["stats"]["average_session"], fonts["body"],
                           COLORS["text_black"], width // 2, 1250,
                           alpha=alpha2)
        draw_text_centered(surface, format_time(stats["averageSessionLength"]), fonts["header"], COLORS["text_black"],
                           width // 2, 1350, alpha=alpha2)


def slide_3_ratings(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_black"]
    surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Rating Spread" if not lang else lang["stats"]["title3"], fonts["title"],
                       COLORS["bg_green"], width // 2, 200, alpha=alpha_title)
    ratings = [stats["oneStar"], stats["twoStars"], stats["threeStars"], stats["fourStars"], stats["fiveStars"]]
    labels = ["1", "2", "3", "4", "5"]
    max_val = max(ratings) if max(ratings) > 0 else 1
    bar_width = 120
    gap = 40
    start_x = (width - ((bar_width * 5) + (gap * 4))) // 2
    base_y = 1300
    max_height = 700
    for i, count in enumerate(ratings):
        local_progress = max(0, min(1, (progress - 0.1) * 1.5))
        ease = ease_out_cubic(local_progress)
        target_h = (count / max_val) * max_height
        current_h = target_h * ease
        x = start_x + (i * (bar_width + gap))
        rect = pygame.Rect(x, base_y - current_h, bar_width, current_h)
        pygame.draw.rect(surface, COLORS["bg_purple"], rect, border_radius=15)
        alpha_label = get_text_alpha(progress, delay_start=0.1 + (i * 0.05), fade_duration=0.5)
        draw_text_centered(surface, labels[i], fonts["body"], COLORS["text_white"], x + bar_width // 2 - 25,
                           base_y + 60, alpha=alpha_label)
        draw_text_centered(surface, "⭐", fonts["emoji"], COLORS["text_white"], x + bar_width // 2 + 25, base_y + 60,
                           alpha=alpha_label)
        if ease > 0.8:
            alpha_count = get_text_alpha(progress, delay_start=0.5, fade_duration=0.5)
            draw_text_centered(surface, str(count), fonts["header"], COLORS["text_white"], x + bar_width // 2,
                               base_y - current_h - 40, alpha=alpha_count)
    alpha_avg = get_text_alpha(progress, delay_start=0.7, fade_duration=0.5)
    draw_text_centered(surface,
                       f"Avg Rating: {stats["averageRating"]:.2f}" if not lang else lang["stats"]["avg_rating"].format(
                           f"{stats["averageRating"]:.2f}"), fonts["header"], COLORS["accent_yellow"],
                       width // 2, 1600, alpha=alpha_avg)


def slide_4_taste_profile(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_pink"]
    surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Your Taste Profile" if not lang else lang["stats"]["title4"], fonts["title"],
                       COLORS["text_black"], width // 2, 250,
                       alpha=alpha_title)
    metrics = [("Relatability" if not lang else lang["voting"]["relatability"], stats["averageRelatability"]),
               ("Lyrics Quality" if not lang else lang["voting"]["lyrics_quality"], stats["averageLyricsQuality"]),
               ("Beat Quality" if not lang else lang["voting"]["beat_quality"], stats["averageBeatQuality"]),
               ("Beat Taste" if not lang else lang["voting"]["beat_taste"], stats["averageBeatTaste"])]
    start_y = 600
    bar_w = 700
    bar_h = 60
    bar_x = (width - bar_w) // 2
    for i, (label, score) in enumerate(metrics):
        local_progress = max(0, min(1, (progress - (i * 0.15)) * 1.5))
        ease = ease_out_cubic(local_progress)
        y = start_y + (i * 250)
        alpha_label = get_text_alpha(progress, delay_start=i * 0.15, fade_duration=0.2)
        draw_text_centered(surface, label, fonts["header"], COLORS["text_black"], width // 2, y - 60, alpha=alpha_label)
        draw_horizontal_bar(surface, bar_x, y, bar_w, bar_h, (score / 5.0) * ease, COLORS["bg_purple"],
                            COLORS["text_white"])
        alpha_score = get_text_alpha(progress, delay_start=i * 0.15 + 0.5, fade_duration=0.2)
        if ease > 0.9:
            draw_text_centered(surface, f"{score:.1f}", fonts["body"], COLORS["text_black"], bar_x + bar_w + 80,
                               y + bar_h // 2, alpha=alpha_score)


def slide_5_peaks_pits(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_orange"]
    surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "The Peaks & Pits" if not lang else lang["stats"]["title5"], fonts["title"],
                       COLORS["text_black"], width // 2, 200,
                       alpha=alpha_title)
    y_good = 500
    alpha_good_header = get_text_alpha(progress, delay_start=0.1, fade_duration=0.5)
    alpha_good_body1 = get_text_alpha(progress, delay_start=0.15, fade_duration=0.5)
    alpha_good_body2 = get_text_alpha(progress, delay_start=0.2, fade_duration=0.5)
    alpha_good_body3 = get_text_alpha(progress, delay_start=0.25, fade_duration=0.5)
    alpha_good_body4 = get_text_alpha(progress, delay_start=0.3, fade_duration=0.5)
    if progress > 0.1:
        draw_text_centered(surface, "--- PEAKS ---" if not lang else lang["stats"]["peaks"], fonts["header"],
                           COLORS["text_white"], width // 2, y_good,
                           alpha=alpha_good_header)
        draw_text_centered(surface, "Most Relatable:" if not lang else lang["stats"]["most_relatable1"],
                           fonts["body_small"], COLORS["text_black"], width // 2,
                           y_good + 80, alpha=alpha_good_body1)
        draw_text_centered(surface, stats["mostRelatable"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_good + 140, alpha=alpha_good_body1)
    if progress > 0.15:
        draw_text_centered(surface, "Best Lyrics:" if not lang else lang["stats"]["best_lyrics1"], fonts["body_small"],
                           COLORS["text_black"], width // 2,
                           y_good + 200, alpha=alpha_good_body2)
        draw_text_centered(surface, stats["bestLyrics"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_good + 260, alpha=alpha_good_body2)
    if progress > 0.2:
        draw_text_centered(surface, "Best Beat:" if not lang else lang["stats"]["best_beat"], fonts["body_small"],
                           COLORS["text_black"], width // 2,
                           y_good + 320, alpha=alpha_good_body3)
        draw_text_centered(surface, stats["bestBeat"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_good + 380, alpha=alpha_good_body3)
    if progress > 0.25:
        draw_text_centered(surface, "Tastiest:" if not lang else lang["stats"]["tastiest1"], fonts["body_small"],
                           COLORS["text_black"], width // 2,
                           y_good + 440, alpha=alpha_good_body4)
        draw_text_centered(surface, stats["tastiest"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_good + 500, alpha=alpha_good_body4)
    y_bad = 1200
    alpha_bad_header = get_text_alpha(progress, delay_start=0.35, fade_duration=0.5)
    alpha_bad_body1 = get_text_alpha(progress, delay_start=0.4, fade_duration=0.5)
    alpha_bad_body2 = get_text_alpha(progress, delay_start=0.45, fade_duration=0.5)
    alpha_bad_body3 = get_text_alpha(progress, delay_start=0.5, fade_duration=0.5)
    alpha_bad_body4 = get_text_alpha(progress, delay_start=0.55, fade_duration=0.5)
    if progress > 0.3:
        draw_text_centered(surface, "--- PITS ---" if not lang else lang["stats"]["pits"], fonts["header"],
                           COLORS["text_white"], width // 2, y_bad,
                           alpha=alpha_bad_header)
        draw_text_centered(surface, "Least Relatable:" if not lang else lang["stats"]["least_relatable"],
                           fonts["body_small"], COLORS["text_black"],
                           width // 2, y_bad + 80, alpha=alpha_bad_body1)
        draw_text_centered(surface, stats["leastRelatable"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_bad + 140, alpha=alpha_bad_body1)
    if progress > 0.35:
        draw_text_centered(surface, "Worst Lyrics:" if not lang else lang["stats"]["worst_lyrics"], fonts["body_small"],
                           COLORS["text_black"],
                           width // 2, y_bad + 200, alpha=alpha_bad_body2)
        draw_text_centered(surface, stats["worstLyrics"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_bad + 260, alpha=alpha_bad_body2)
    if progress > 0.4:
        draw_text_centered(surface, "Worst Beat:" if not lang else lang["stats"]["worst_beat"], fonts["body_small"],
                           COLORS["text_black"],
                           width // 2, y_bad + 320, alpha=alpha_bad_body3)
        draw_text_centered(surface, stats["worstBeat"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_bad + 380, alpha=alpha_bad_body3)
    if progress > 0.45:
        draw_text_centered(surface, "Most Disgusting:" if not lang else lang["stats"]["most_disgusting"],
                           fonts["body_small"], COLORS["text_black"],
                           width // 2, y_bad + 440, alpha=alpha_bad_body4)
        draw_text_centered(surface, stats["mostDisgusting"], fonts["body_bold"], COLORS["text_black"], width // 2,
                           y_bad + 500, alpha=alpha_bad_body4)


def slide_6_artist(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_purple"]
    surface.fill(bg)
    artist_data = [("Most Starred" if not lang else lang["stats"]["most_starred"], stats["mostStarredArtists"]),
                   ("Most Relatable" if not lang else lang["stats"]["most_relatable2"], stats["mostRelatableArtists"]),
                   ("Best Lyrics" if not lang else lang["stats"]["best_lyrics2"], stats["bestLyricsArtists"]),
                   ("Best Produced" if not lang else lang["stats"]["best_produced"], stats["bestProducedArtists"]),
                   ("Tastiest" if not lang else lang["stats"]["tastiest2"], stats["tastiestArtists"])]
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Your Top Artists" if not lang else lang["stats"]["title6"], fonts["title"],
                       COLORS["accent_yellow"], width // 2, 200,
                       alpha=alpha_title)
    draw_text_centered(surface, "Across All Categories" if not lang else lang["stats"]["all_categories"],
                       fonts["header"], COLORS["text_white"], width // 2, 350,
                       alpha=alpha_title)
    start_y = 550
    item_spacing = 250
    fade_delay_increment = 0.1
    for i, (category, artist) in enumerate(artist_data):
        y = start_y + (i * item_spacing)
        category_delay = 0.1 + (i * fade_delay_increment)
        artist_delay = category_delay + 0.05
        alpha_category = get_text_alpha(progress, delay_start=category_delay, fade_duration=0.5)
        alpha_artist = get_text_alpha(progress, delay_start=artist_delay, fade_duration=0.5)
        draw_text_centered(surface, category, fonts["header"], COLORS["text_black"], width // 2, y,
                           alpha=alpha_category)
        draw_text_centered(surface, artist.upper(), fonts["header_big"], COLORS["text_white"], width // 2, y + 100,
                           alpha=alpha_artist)


def slide_7_voting_habits(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_green"]
    surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Listening vs Voting" if not lang else lang["stats"]["title7"], fonts["title"],
                       COLORS["bg_darkblue"], width // 2, 200,
                       alpha=alpha_title)
    total_interaction = stats["timeListening"] + stats["timeVoting"]
    if total_interaction == 0:
        listen_percent = 0
        vote_percent = 0
    else:
        listen_percent = stats["timeListening"] / total_interaction
        vote_percent = stats["timeVoting"] / total_interaction
    bar_y = 450
    bar_h = 150
    bar_w_total = 800
    bar_x = (width - bar_w_total) // 2
    ease = ease_out_cubic(min(1, progress * 1.5))
    total_w_animated = bar_w_total * ease
    listen_w = total_w_animated * listen_percent
    pygame.draw.rect(surface, COLORS["bg_darkblue"], (bar_x, bar_y, listen_w, bar_h), border_radius=20)
    alpha_listen = get_text_alpha(progress, delay_start=0.3, fade_duration=0.5)
    if ease > 0.3 and listen_w > 150:
        draw_text_centered(surface, f"Listening: {int(listen_percent * 100)}%" if not lang else lang["stats"][
            "listening"].format(str(int(listen_percent * 100))), fonts["body"], COLORS["text_white"],
                           bar_x + listen_w // 2, bar_y + bar_h // 2, alpha=alpha_listen)
    vote_start_x = bar_x + listen_w
    vote_w = total_w_animated * vote_percent
    pygame.draw.rect(surface, COLORS["bg_pink"], (vote_start_x, bar_y, vote_w, bar_h), border_radius=20)
    alpha_vote = get_text_alpha(progress, delay_start=0.8, fade_duration=0.5)
    if ease > 0.8 and vote_w > 150:
        draw_text_centered(surface,
                           f"Voting: {int(vote_percent * 100)}%" if not lang else lang["stats"]["voting"].format(
                               str(int(vote_percent * 100))), fonts["body"], COLORS["text_black"],
                           vote_start_x + vote_w // 2, bar_y + bar_h // 2, alpha=alpha_vote)
    y_stats = 800
    stats_list = [
        f"Tracks Rated: {stats["tracksRated"]}" if not lang else lang["stats"]["tracks_rated"].format(
            str(stats["tracksRated"])),
        f"Tracks Replayed: {stats["replays"]}" if not lang else lang["stats"]["replayed"].format(str(stats["replays"])),
        f"Time Listening: {int(stats["timeListening"] / 60)} mins" if not lang else lang["stats"][
            "time_listening"].format(str(int(stats["timeListening"] / 60))),
        f"Time Voting: {int(stats["timeVoting"] / 60)} mins" if not lang else lang["stats"]["time_voting"].format(
            str(int(stats["timeVoting"] / 60))),
        f"Avg Track Length: {format_time(stats["averageTrackLength"])}" if not lang else lang["stats"][
            "average_track_length"].format(str(format_time(stats["averageTrackLength"]))),
        f"Avg Listening Time: {format_time(stats["averageTimeListened"])}" if not lang else lang["stats"][
            "average_time_listened"].format(str(format_time(stats["averageTimeListened"]))),
        f"Avg Voting Time: {format_time(stats["averageTimeVoting"])}" if not lang else lang["stats"][
            "average_time_voting"].format(str(format_time(stats["averageTimeVoting"])))
    ]
    for i, line in enumerate(stats_list):
        alpha_text = get_text_alpha(progress, delay_start=0.3 + (i * 0.1), fade_duration=0.5)
        draw_text_centered(surface, line, fonts["header"], COLORS["bg_darkblue"], width // 2, y_stats + (i * 150),
                           alpha=alpha_text)


def slide_8_winner(surface, progress, fonts, stats, playlist):
    bg = COLORS["bg_black"]
    surface.fill(bg)
    positive_categories = {
        "bestBeat": "Best Beat" if not lang else lang["stats"]["best_produced"],
        "bestLyrics": "Best Lyrics" if not lang else lang["stats"]["best_lyrics2"],
        "mostRelatable": "Most Relatable" if not lang else lang["stats"]["most_relatable2"],
        "tastiest": "Tastiest Track" if not lang else lang["stats"]["tastiest2"]
    }
    candidates = {}
    for key, label in positive_categories.items():
        track = stats.get(key)
        if track:
            if track not in candidates:
                candidates[track] = {"count": 0, "reasons": []}
            candidates[track]["count"] += 1
            candidates[track]["reasons"].append(label)
    if not candidates:
        winner_track = "No Data" if not lang else lang["stats"]["no_data"]
        winner_reasons = []
    else:
        sorted_candidates = sorted(candidates.items(), key=lambda item: item[1]["count"], reverse=True)
        winner_track = sorted_candidates[0][0]
        winner_reasons = sorted_candidates[0][1]["reasons"]
    parts = winner_track.split(" - ", 1)
    track_artist = parts[0]
    track_name = parts[1]
    if len(winner_reasons) == 4:
        subtitle_text = "The Ultimate Masterpiece (Swept All Categories!)" if not lang else lang["stats"]["masterpiece"]
    elif len(winner_reasons) == 3:
        subtitle_text = "Triple Crown Winner!" if not lang else lang["stats"]["triple_crown"]
    elif len(winner_reasons) > 0:
        subtitle_text = " & ".join(winner_reasons)
    else:
        subtitle_text = "Top Rated Track" if not lang else lang["stats"]["top_rated"]
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "The Golden Track" if not lang else lang["stats"]["title8"], fonts["title"],
                       COLORS["bg_green"], width // 2, 250,
                       alpha=alpha_title)
    center = (width // 2, 800)
    radius = 300 * ease_out_cubic(min(1, progress * 2))
    pygame.draw.circle(surface, (30, 30, 30), center, radius)
    pygame.draw.circle(surface, COLORS["bg_pink"], center, radius * 0.35)
    rot_x = center[0] + math.cos(progress * 4) * (radius * 0.8)
    rot_y = center[1] + math.sin(progress * 4) * (radius * 0.8)
    if radius > 0:
        pygame.draw.circle(surface, (220, 220, 220), (rot_x, rot_y), 15)
    if progress > 0.5:
        anim_y = 100 * (1 - ease_out_cubic((progress - 0.5) * 2))
        alpha_track_name = get_text_alpha(progress, delay_start=0.5, fade_duration=0.5)
        alpha_track_artist = get_text_alpha(progress, delay_start=0.6, fade_duration=0.5)
        alpha_combo = get_text_alpha(progress, delay_start=0.7, fade_duration=0.5)
        draw_text_centered(surface, track_name, fonts["header_big"], COLORS["text_white"], width // 2, 1250 + anim_y,
                           alpha=alpha_track_name)
        draw_text_centered(surface, track_artist, fonts["header"], COLORS["bg_purple"], width // 2, 1400 + anim_y,
                           alpha=alpha_track_artist)
        draw_text_centered(surface, subtitle_text, fonts["body"], COLORS["text_white"], width // 2, 1600 + anim_y,
                           alpha=alpha_combo)
    elapsed_time = progress * animation_base_speed
    fade_start_time = 7 - 1
    if elapsed_time > fade_start_time:
        local_fade_progress = (elapsed_time - fade_start_time) / 1
        local_fade_progress = min(1.0, max(0.0, local_fade_progress))
        alpha = int(local_fade_progress * 255)
        fade_surf = pygame.Surface((width, height))
        fade_surf.fill(COLORS["bg_black"])
        fade_surf.set_alpha(alpha)
        surface.blit(fade_surf, (0, 0))


def render_wrapped(stats, playlist):
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.HIDDEN)

    fonts = {
        "mega_big": pygame.font.Font(os.path.join("resources", "fonts", "NotoSans.ttf"), 170),
        "mega": pygame.font.Font(os.path.join("resources", "fonts", "NotoSans.ttf"), 130),
        "title": pygame.font.Font(os.path.join("resources", "fonts", "NotoSans.ttf"), 90),
        "header_big": pygame.font.Font(os.path.join("resources", "fonts", "NotoSansBold.ttf"), 80),
        "header": pygame.font.Font(os.path.join("resources", "fonts", "NotoSansBold.ttf"), 60),
        "body_bold": pygame.font.Font(os.path.join("resources", "fonts", "NotoSansBold.ttf"), 45),
        "body": pygame.font.Font(os.path.join("resources", "fonts", "NotoSans.ttf"), 45),
        "body_small": pygame.font.Font(os.path.join("resources", "fonts", "NotoSans.ttf"), 35),
        "emoji": pygame.font.Font(os.path.join("resources", "fonts", "NotoEmoji.ttf"), 45)
    }
    slides = [
        slide_1_intro, slide_2_sessions, slide_3_ratings, slide_4_taste_profile,
        slide_5_peaks_pits, slide_6_artist, slide_7_voting_habits, slide_8_winner
    ]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(f"wrapped_{playlist}.mp4", fourcc, fps, (width, height))
    surf_current = pygame.Surface((width, height))
    surf_next = pygame.Surface((width, height))
    print(f"Generating your wrapped for {playlist}" if not lang else lang["stats"]["waiting"]["started"].format(
        str(playlist)))
    frames_per_transition = int(transition_duration * fps)
    for i in range(len(slides)):
        current_slide_func = slides[i]
        duration = slide_durations.get(i, default_slide_duration)
        frames_per_slide = int(duration * fps)
        print(f"On Slide {i + 1}" if not lang else lang["stats"]["waiting"]["slide"].format(str(i + 1)))
        next_slide_func = slides[(i + 1) % len(slides)] if i + 1 < len(slides) else None
        for f in range(frames_per_slide):
            elapsed_time = f / fps
            anim_progress = elapsed_time / animation_base_speed
            current_slide_func(screen, anim_progress, fonts, stats, playlist)
            view = pygame.surfarray.array3d(screen).transpose([1, 0, 2])
            frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
            video.write(frame)
            pygame.event.pump()
        if next_slide_func:
            for f in range(frames_per_transition):
                trans_progress = f / frames_per_transition
                ease = ease_in_out_sin(trans_progress)
                current_slide_func(surf_current, 2.0, fonts, stats, playlist)
                next_slide_func(surf_next, 0.0, fonts, stats, playlist)
                screen.fill((0, 0, 0))
                screen.blit(surf_current, (0, -int(height * ease)))
                screen.blit(surf_next, (0, height - int(height * ease)))
                view = pygame.surfarray.array3d(screen).transpose([1, 0, 2])
                frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
                video.write(frame)
                pygame.event.pump()
    video.release()
    pygame.quit()
    print(f"Done! Let's view!" if not lang else lang["stats"]["waiting"]["finished"])


if __name__ == "__main__":
    from pprint import pprint

    pprint(calculateStats(), sort_dicts=False, indent=4)
