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


width, height = 1920, 1080
settings_json = misc.load_settings()
fps = max(min(settings_json["fps"], 240), 20)
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
lang = misc.load_language(settings_json)


def draw_text_centered(surface, text, font, color, center_x, center_y, alpha=255, shadow=False, return_pos=False):
    if shadow:
        for offset in range(3):
            text_obj_shadow = font.render(text, True, (100, 100, 100))
            if alpha < 255:
                text_obj_shadow.set_alpha(max(alpha - 100, 0))
            rect_shadow = text_obj_shadow.get_rect(center=(center_x + 3, center_y + offset + 1))
            surface.blit(text_obj_shadow, rect_shadow)
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
        pygame.draw.rect(surface, color, (x, y, min(actual_w + 2, w), h), border_radius=h // 2)


def lerp_color(color_start, color_end, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(color_start, color_end))


def slide_1_intro(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_purple"]
    if draw_bg:
        surface.fill(bg)
    anim_y = 100 * (1 - ease_out_cubic(min(progress * 2, 1)))
    draw_text_centered(surface, "Wrapped" if not lang else lang["stats"]["title"], fonts["mega"],
                       COLORS["accent_yellow"], width // 2, 200 + anim_y, shadow=True)
    draw_text_centered(surface, playlist, fonts["title"], COLORS["text_black"], width // 2,
                       350 + anim_y, shadow=True)
    stats_txt = [
        f"{stats["sessionCount"]} Sessions" if not lang else lang["stats"]["sessions"].format(
            str(stats["sessionCount"])),
        f"{stats["daysUsed"]} Days Active" if not lang else lang["stats"]["active_days"].format(str(stats["daysUsed"])),
        f"Total Time: {int(stats["timeTotal"] / 60)} mins" if not lang else lang["stats"]["total_time"].format(
            str(int(stats["timeTotal"] / 60)))
    ]
    positions_x = [width // 4, width // 2, width * 3 // 4]
    start_y = 700
    for i, line in enumerate(stats_txt):
        local_progress = max(0, min(1, (progress - (i * 0.15)) * 2))
        ease = ease_out_cubic(local_progress)
        offset_y = (1 - ease) * (height - start_y + 100)
        if local_progress > 0:
            draw_text_centered(surface, line, fonts["header"], COLORS["text_white"],
                               positions_x[i], start_y + offset_y, shadow=True)


def slide_2_sessions(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_darkblue"]
    if draw_bg:
        surface.fill(bg)
    alpha = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Deep Dive Sessions" if not lang else lang["stats"]["title2"], fonts["title"],
                       COLORS["bg_green"], width // 2, 150, alpha=alpha, shadow=True)
    scale1 = ease_out_cubic(min(1, progress * 1.5))
    center_x1 = width // 4
    center_y1 = 600
    radius1 = 250
    pygame.draw.circle(surface, COLORS["bg_pink"], (center_x1, center_y1), radius1 * scale1)
    alpha1 = get_text_alpha(progress, delay_start=0.2, fade_duration=0.5)
    if progress > 0.2:
        draw_text_centered(surface, "Longest Session" if not lang else lang["stats"]["longest_session"], fonts["body"],
                           COLORS["text_black"], center_x1, center_y1 - 100,
                           alpha=alpha1)
        draw_text_centered(surface, format_time(stats["longestSessionLength"]), fonts["header_big"],
                           COLORS["text_black"], center_x1, center_y1 + 20, alpha=alpha1)
    scale2 = ease_out_cubic(max(0, min(1, (progress - 0.5) * 1.5)))
    center_x2 = width * 3 // 4
    center_y2 = 600
    radius2 = 200
    pygame.draw.circle(surface, COLORS["bg_orange"], (center_x2, center_y2), radius2 * scale2)
    alpha2 = get_text_alpha(progress, delay_start=0.75, fade_duration=0.5)
    if progress > 0.75:
        draw_text_centered(surface, "Average Session" if not lang else lang["stats"]["average_session"], fonts["body"],
                           COLORS["text_black"], center_x2, center_y2 - 80,
                           alpha=alpha2)
        draw_text_centered(surface, format_time(stats["averageSessionLength"]), fonts["header"], COLORS["text_black"],
                           center_x2, center_y2, alpha=alpha2)


def slide_3_ratings(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_black"]
    if draw_bg:
        surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Rating Spread" if not lang else lang["stats"]["title3"], fonts["title"],
                       COLORS["bg_green"], width // 2, 150, alpha=alpha_title, shadow=True)
    ratings = [stats["oneStar"], stats["twoStars"], stats["threeStars"], stats["fourStars"], stats["fiveStars"]]
    labels = ["1", "2", "3", "4", "5"]
    max_val = max(ratings) if max(ratings) > 0 else 1
    bar_width = 200
    gap = 70
    start_x = (width - ((bar_width * 5) + (gap * 4))) // 2
    base_y = 850
    max_height = 500
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
                       width // 2, 1000, alpha=alpha_avg)


def slide_4_taste_profile(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_pink"]
    if draw_bg:
        surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Your Taste Profile" if not lang else lang["stats"]["title4"], fonts["title"],
                       COLORS["text_black"], width // 2, 150, alpha=alpha_title, shadow=True)
    metrics = [("Relatability" if not lang else lang["voting"]["relatability"], stats["averageRelatability"]),
               ("Lyrics Quality" if not lang else lang["voting"]["lyrics_quality"], stats["averageLyricsQuality"]),
               ("Beat Quality" if not lang else lang["voting"]["beat_quality"], stats["averageBeatQuality"]),
               ("Beat Taste" if not lang else lang["voting"]["beat_taste"], stats["averageBeatTaste"])]
    start_y = 350
    bar_w = 1200
    bar_h = 60
    bar_x = (width - bar_w) // 2
    item_spacing = 180
    for i, (label, score) in enumerate(metrics):
        local_progress = max(0, min(1, (progress - (i * 0.15)) * 1.5))
        ease = ease_out_cubic(local_progress)
        y = start_y + (i * item_spacing)
        alpha_label = get_text_alpha(progress, delay_start=i * 0.15, fade_duration=0.2)
        draw_text_centered(surface, label, fonts["header"], COLORS["text_black"], width // 2, y - 50, alpha=alpha_label)
        draw_horizontal_bar(surface, bar_x, y, bar_w, bar_h, (score / 5.0) * ease, COLORS["bg_purple"],
                            COLORS["text_white"])
        alpha_score = get_text_alpha(progress, delay_start=i * 0.15 + 0.5, fade_duration=0.2)
        if ease > 0.9:
            draw_text_centered(surface, f"{score:.1f}", fonts["body"], COLORS["text_black"], bar_x + bar_w + 80,
                               y + bar_h // 2, alpha=alpha_score)


def slide_5_peaks_pits(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_orange"]
    if draw_bg:
        surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "The Peaks & Pits" if not lang else lang["stats"]["title5"], fonts["title"],
                       COLORS["text_black"], width // 2, 150, alpha=alpha_title, shadow=True)
    x_good = width // 4
    x_bad = width * 3 // 4
    y_header = 300
    alpha_good_header = get_text_alpha(progress, delay_start=0.1, fade_duration=0.5)
    alpha_bad_header = get_text_alpha(progress, delay_start=0.35, fade_duration=0.5)
    draw_text_centered(surface, "--- PEAKS ---" if not lang else lang["stats"]["peaks"], fonts["header"],
                       COLORS["text_white"], x_good, y_header, alpha=alpha_good_header, shadow=True)
    draw_text_centered(surface, "--- PITS ---" if not lang else lang["stats"]["pits"], fonts["header"],
                       COLORS["text_white"], x_bad, y_header, alpha=alpha_bad_header, shadow=True)
    peaks = [
        ("Most Relatable:" if not lang else lang["stats"]["most_relatable1"], stats["mostRelatable"], 0.15),
        ("Best Lyrics:" if not lang else lang["stats"]["best_lyrics1"], stats["bestLyrics"], 0.2),
        ("Best Beat:" if not lang else lang["stats"]["best_beat"], stats["bestBeat"], 0.25),
        ("Tastiest:" if not lang else lang["stats"]["tastiest1"], stats["tastiest"], 0.3)
    ]
    pits = [
        ("Least Relatable:" if not lang else lang["stats"]["least_relatable"], stats["leastRelatable"], 0.4),
        ("Worst Lyrics:" if not lang else lang["stats"]["worst_lyrics"], stats["worstLyrics"], 0.45),
        ("Worst Beat:" if not lang else lang["stats"]["worst_beat"], stats["worstBeat"], 0.5),
        ("Most Disgusting:" if not lang else lang["stats"]["most_disgusting"], stats["mostDisgusting"], 0.55)
    ]
    y_start = 420
    y_spacing = 160
    for i, (label, track, delay) in enumerate(peaks):
        alpha = get_text_alpha(progress, delay_start=delay, fade_duration=0.5)
        y = y_start + (i * y_spacing)
        if progress > delay:
            draw_text_centered(surface, label, fonts["body_small"], COLORS["text_black"], x_good, y, alpha=alpha)
            draw_text_centered(surface, track, fonts["body_bold"], COLORS["text_black"], x_good, y + 60, alpha=alpha)
    for i, (label, track, delay) in enumerate(pits):
        alpha = get_text_alpha(progress, delay_start=delay, fade_duration=0.5)
        y = y_start + (i * y_spacing)
        if progress > delay:
            draw_text_centered(surface, label, fonts["body_small"], COLORS["text_black"], x_bad, y, alpha=alpha)
            draw_text_centered(surface, track, fonts["body_bold"], COLORS["text_black"], x_bad, y + 60, alpha=alpha)


def slide_6_artist(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_purple"]
    if draw_bg:
        surface.fill(bg)
    artist_data = [("Most Relatable" if not lang else lang["stats"]["most_relatable2"], stats["mostRelatableArtists"]),
                   ("Best Lyrics" if not lang else lang["stats"]["best_lyrics2"], stats["bestLyricsArtists"]),
                   ("Best Produced" if not lang else lang["stats"]["best_produced"], stats["bestProducedArtists"]),
                   ("Tastiest" if not lang else lang["stats"]["tastiest2"], stats["tastiestArtists"]),
                   ("Most Starred" if not lang else lang["stats"]["most_starred"], stats["mostStarredArtists"])]
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Your Top Artists" if not lang else lang["stats"]["title6"], fonts["title"],
                       COLORS["accent_yellow"], width // 2, 100, alpha=alpha_title, shadow=True)
    draw_text_centered(surface, "Across All Categories" if not lang else lang["stats"]["all_categories"],
                       fonts["header"], COLORS["text_white"], width // 2, 250, alpha=alpha_title, shadow=True)
    positions = [(width // 4, 400), (width * 3 // 4, 400), (width // 4, 650), (width * 3 // 4, 650), (width // 2, 900)]
    fade_delay_increment = 0.1
    for i, (category, artist) in enumerate(artist_data):
        x, y = positions[i]
        category_delay = 0.1 + (i * fade_delay_increment)
        artist_delay = category_delay + 0.05
        alpha_category = get_text_alpha(progress, delay_start=category_delay, fade_duration=0.5)
        alpha_artist = get_text_alpha(progress, delay_start=artist_delay, fade_duration=0.5)
        draw_text_centered(surface, category, fonts["header"], COLORS["text_black"], x, y,
                           alpha=alpha_category)
        draw_text_centered(surface, artist.upper(), fonts["header_big"], COLORS["text_white"], x, y + 70,
                           alpha=alpha_artist, shadow=True)


def slide_7_voting_habits(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_green"]
    if draw_bg:
        surface.fill(bg)
    alpha_title = get_text_alpha(progress, delay_start=0.0, fade_duration=0.5)
    draw_text_centered(surface, "Listening vs Voting" if not lang else lang["stats"]["title7"], fonts["title"],
                       COLORS["bg_darkblue"], width // 2, 150, alpha=alpha_title, shadow=True)
    total_interaction = stats["timeListening"] + stats["timeVoting"]
    if total_interaction == 0:
        listen_percent = 0
        vote_percent = 0
    else:
        listen_percent = stats["timeListening"] / total_interaction
        vote_percent = stats["timeVoting"] / total_interaction
    bar_y = 350
    bar_h = 150
    bar_w_total = 1400
    bar_x = (width - bar_w_total) // 2
    ease = ease_out_cubic(min(1, progress * 1.5))
    total_w_animated = bar_w_total * ease
    listen_w = total_w_animated * listen_percent
    pygame.draw.rect(surface, COLORS["bg_darkblue"], (bar_x, bar_y, listen_w, bar_h), border_radius=20)
    alpha_listen = get_text_alpha(progress, delay_start=0.3, fade_duration=0.5)
    temp_text = fonts["body"].render(
        f"Listening: {int(listen_percent * 100)}%" if not lang else lang["stats"][
            "listening"].format(str(int(listen_percent * 100))), True, COLORS["text_black"])
    if ease > 0.3 and temp_text.get_width() < listen_w + 25:
        draw_text_centered(surface, f"Listening: {int(listen_percent * 100)}%" if not lang else lang["stats"][
            "listening"].format(str(int(listen_percent * 100))), fonts["body"], COLORS["text_white"],
                           bar_x + listen_w // 2, bar_y + bar_h // 2, alpha=alpha_listen)
    vote_start_x = bar_x + listen_w
    vote_w = total_w_animated * vote_percent
    pygame.draw.rect(surface, COLORS["bg_pink"], (vote_start_x, bar_y, vote_w, bar_h), border_radius=20)
    alpha_vote = get_text_alpha(progress, delay_start=0.8, fade_duration=0.5)
    temp_text = fonts["body"].render(
        f"Voting: {int(vote_percent * 100)}%" if not lang else lang["stats"]["voting"].format(
            str(int(vote_percent * 100))), True, COLORS["text_black"])
    if ease > 0.8 and temp_text.get_width() < vote_w + 25:
        draw_text_centered(surface,
                           f"Voting: {int(vote_percent * 100)}%" if not lang else lang["stats"]["voting"].format(
                               str(int(vote_percent * 100))), fonts["body"], COLORS["text_black"],
                           vote_start_x + vote_w // 2, bar_y + bar_h // 2, alpha=alpha_vote)
    y_stats_start = 600
    x_col1 = width // 4
    x_col2 = width * 3 // 4
    x_row4 = (x_col1 + x_col2) // 2
    y_spacing = 120
    stats_list = [
        f"Tracks Rated: {stats["tracksRated"]}" if not lang else lang["stats"]["tracks_rated"].format(
            str(stats["tracksRated"])),
        f"Time Listening: {int(stats["timeListening"] / 60)} mins" if not lang else lang["stats"][
            "time_listening"].format(str(int(stats["timeListening"] / 60))),
        f"Avg Time Listening: {format_time(stats["averageTimeListened"])}" if not lang else lang["stats"][
            "average_time_listened"].format(str(format_time(stats["averageTimeListened"]))),
        f"Avg Track Length: {format_time(stats["averageTrackLength"])}" if not lang else lang["stats"][
            "average_track_length"].format(str(format_time(stats["averageTrackLength"]))),
        f"Tracks Replayed: {stats["replays"]}" if not lang else lang["stats"]["replayed"].format(str(stats["replays"])),
        f"Time Voting: {int(stats["timeVoting"] / 60)} mins" if not lang else lang["stats"]["time_voting"].format(
            str(int(stats["timeVoting"] / 60))),
        f"Avg Time Voting: {format_time(stats["averageTimeVoting"])}" if not lang else lang["stats"][
            "average_time_voting"].format(str(format_time(stats["averageTimeVoting"])))
    ]
    for i, line in enumerate(stats_list):
        is_col1 = i < 4
        is_row4 = i == 3
        if is_col1 and not is_row4:
            x = x_col1
        elif not is_col1 and not is_row4:
            x = x_col2
        elif is_col1 and is_row4:
            x = x_row4
        y_index = i if is_col1 else i - 4
        y = y_stats_start + (y_index * y_spacing)
        alpha_text = get_text_alpha(progress, delay_start=0.3 + (i * 0.1), fade_duration=0.5)
        draw_text_centered(surface, line, fonts["header"], COLORS["bg_darkblue"], x, y,
                           alpha=alpha_text)


def slide_8_winner(surface, progress, fonts, stats, playlist, draw_bg=True):
    bg = COLORS["bg_black"]
    if draw_bg:
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
    draw_text_centered(surface, "Your Golden Track" if not lang else lang["stats"]["title8"], fonts["title"],
                       COLORS["bg_green"], width // 2, 150, alpha=alpha_title, shadow=True)
    center = (width // 2, 500)
    radius = 200 * ease_out_cubic(min(1, progress * 2))
    pygame.draw.circle(surface, (30, 30, 30), center, radius)
    pygame.draw.circle(surface, COLORS["bg_pink"], center, radius * 0.35)
    rot_x = center[0] + math.cos(progress * 4) * (radius * 0.8)
    rot_y = center[1] + math.sin(progress * 4) * (radius * 0.8)
    if radius > 0:
        pygame.draw.circle(surface, (220, 220, 220), (rot_x, rot_y), 10)
    if progress > 0.5:
        anim_y = 100 * (1 - ease_out_cubic((progress - 0.5) * 2))
        alpha_track_name = get_text_alpha(progress, delay_start=0.5, fade_duration=0.5)
        alpha_track_artist = get_text_alpha(progress, delay_start=0.6, fade_duration=0.5)
        alpha_combo = get_text_alpha(progress, delay_start=0.7, fade_duration=0.5)
        draw_text_centered(surface, track_name, fonts["header_big"], COLORS["text_white"], width // 2, 850 + anim_y,
                           alpha=alpha_track_name)
        draw_text_centered(surface, track_artist, fonts["header"], COLORS["bg_purple"], width // 2, 950 + anim_y,
                           alpha=alpha_track_artist)
        draw_text_centered(surface, subtitle_text, fonts["body"], COLORS["text_white"], width // 2, 1030 + anim_y,
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


class WrappedPlayer:
    def __init__(self, width, height, stats, playlist):
        self.width = width
        self.height = height
        self.stats = stats
        self.playlist = playlist
        self.fonts = {
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
        self.slides = [
            slide_1_intro, slide_2_sessions, slide_3_ratings, slide_4_taste_profile,
            slide_5_peaks_pits, slide_6_artist, slide_7_voting_habits, slide_8_winner
        ]
        self.current_slide_index = 0
        self.timer = 0.0
        self.is_transitioning = False
        self.transition_timer = 0.0
        self.finished = False
        self.surf_current = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surf_next = pygame.Surface((width, height), pygame.SRCALPHA)
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video = cv2.VideoWriter(f"wrapped_{playlist}.mp4", self.fourcc, fps, (width, height))
        self.slide_colors = [
            COLORS["bg_purple"],
            COLORS["bg_darkblue"],
            COLORS["bg_black"],
            COLORS["bg_pink"],
            COLORS["bg_orange"],
            COLORS["bg_purple"],
            COLORS["bg_green"],
            COLORS["bg_black"]
        ]

    def update(self, dt):
        """
        dt:Time passed since last frame in seconds (e.g., 0.016 for 60fps)
        Returns:
            True if animation is finished, False otherwise
        """
        if self.finished:
            return True
        current_duration = slide_durations.get(self.current_slide_index, default_slide_duration)
        if self.is_transitioning:
            self.transition_timer += dt
            if self.transition_timer >= transition_duration:
                self.is_transitioning = False
                self.transition_timer = 0
                self.current_slide_index += 1
                self.timer = 0
                if self.current_slide_index >= len(self.slides):
                    self.finished = True
        else:
            self.timer += dt
            if self.timer >= current_duration:
                if self.current_slide_index + 1 < len(self.slides):
                    self.is_transitioning = True
                    self.transition_timer = 0
                else:
                    self.finished = True
        return self.finished

    def draw(self, screen):
        if self.finished:
            self.video.release()
            return
        current_slide_func = self.slides[self.current_slide_index]
        if self.is_transitioning:
            next_slide_func = self.slides[self.current_slide_index + 1]
            trans_progress = self.transition_timer / transition_duration
            ease = ease_in_out_sin(trans_progress)
            color_curr = self.slide_colors[self.current_slide_index]
            color_next = self.slide_colors[self.current_slide_index + 1]
            blended_bg = lerp_color(color_curr, color_next, ease)
            screen.fill(blended_bg)
            self.surf_current.fill((0, 0, 0, 0))
            self.surf_next.fill((0, 0, 0, 0))
            # draw current slide at end state (frozen)
            current_slide_func(self.surf_current, 2.0, self.fonts, self.stats, self.playlist, draw_bg=False)
            # draw next slide at start state
            next_slide_func(self.surf_next, 0.0, self.fonts, self.stats, self.playlist, draw_bg=False)
            screen.blit(self.surf_current, (-int(self.width * ease), 0))
            screen.blit(self.surf_next, (self.width - int(self.width * ease), 0))
            view = pygame.surfarray.array3d(screen).transpose([1, 0, 2])
            frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
            self.video.write(frame)
        else:
            # normal slide logic
            anim_progress = self.timer / animation_base_speed
            current_slide_func(screen, anim_progress, self.fonts, self.stats, self.playlist)
            view = pygame.surfarray.array3d(screen).transpose([1, 0, 2])
            frame = cv2.cvtColor(view, cv2.COLOR_RGB2BGR)
            self.video.write(frame)


if __name__ == "__main__":
    from pprint import pprint

    pprint(calculateStats(), sort_dicts=False, indent=4)
