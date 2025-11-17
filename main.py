import logging
import math
import os
import time
import tkinter

import pygame
import pyvidplayer2

import colors
import data
import misc
import settings
import visuals

if misc.isLogEnabled():
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
    log = logging.getLogger()
    log.info("Song Comparator Log:")
    log.info("(You can disable this in the settings.)")
    log.info("")
    log.info("Info: initializing variables")
    last_log = None
    logging = True
else:
    logging = False


def save_log(msg, type: str = None):
    if logging:
        global last_log
        if msg != last_log:
            if type is None or type == "info":
                log.info(f"Info: {msg}")
            elif type == "warning":
                log.warning(f"Warning: {msg}")
            elif type == "error":
                log.error(f"Error: {msg}")
        last_log = msg


def run():
    settings_json = misc.load_settings()
    lang = misc.load_language(settings_json)
    running = True
    esc = 0
    pg = pygame.display.set_mode()
    width, height = pg.get_size()
    pygame.display.set_caption("Song Comparator")
    pygame.display.set_icon(pygame.image.load("resources/assets/icon.png"))
    clock = pygame.time.Clock()
    track = None
    video = None
    coverActive = False
    scaledCover = None
    coverRect = None
    button_font = pygame.font.Font(settings_json["font"], 48)
    emojiFont = pygame.font.Font("resources/fonts/NotoEmoji.ttf", 48)
    main_font = pygame.font.Font(settings_json["font"], 42)
    # need to rate info font
    ntri_font = pygame.font.Font(settings_json["font"], 24)
    note_font = pygame.font.Font(settings_json["font"], 18)
    color_palette = colors.get_colors(f"resources/themes/{settings_json["theme"]}.json")
    base_color = colors.hex_to_rgb(
        color_palette["CTkButton"]["fg_color"][0 if settings_json["appearance_mode"] == "Light" else 1])
    hover_color = colors.hex_to_rgb(
        color_palette["CTkButton"]["hover_color"][0 if settings_json["appearance_mode"] == "Light" else 1])
    click_color = colors.hex_to_rgb(color_palette["palette"]["button_active_bg"])
    disabled_color = colors.hex_to_rgb(
        color_palette["CTkButton"]["fg_color_disabled"][0 if settings_json["appearance_mode"] == "Light" else 1])
    manager = visuals.ButtonManager(button_font)
    manager2 = visuals.ButtonManager(button_font)
    manager3 = visuals.ButtonManager(emojiFont)
    manager4 = visuals.ButtonManager(emojiFont)
    cog_button = manager3.add_button("⚙️", "menu", base_color=base_color, hover_color=hover_color,
                                     click_color=click_color,
                                     disabled_color=disabled_color)
    full_screen_viewport = pygame.Rect(0, 0, width, height)
    title_button_viewport = pygame.Rect(width - 200, height - 200, 200, 200)
    title_viewport = pygame.Rect(0, 100, width, height - 100)
    icon_white = pygame.image.load("resources/assets/icon_white.png")
    icon_white = pygame.transform.smoothscale_by(icon_white, 3)
    icon_white = pygame.transform.smoothscale(icon_white, (icon_white.get_width() // 4, icon_white.get_height() // 4))
    icon_white_height = icon_white.get_height()
    icon_white_width_half = icon_white.get_width() // 2
    icon_white_height_half = icon_white.get_height() // 2
    icon_glow = pygame.image.load("resources/assets/icon_glow.png")
    icon_glow = pygame.transform.smoothscale_by(icon_glow, 3)
    icon_glow = pygame.transform.smoothscale(icon_glow, (icon_glow.get_width() // 4, icon_glow.get_height() // 4))
    icon_glow_width_half = icon_glow.get_width() // 2
    icon_glow_height_half = icon_glow.get_height() // 2
    currentMenu = "main"
    intro = True
    fadein = 0
    y_intro = height // 2 - icon_white_height_half
    init_y_intro = y_intro
    animation_state = 0
    rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)
    mouse_1_up = False
    wasSingleTrack = False
    playedSongOnce = False
    playlist = None
    coverIndex = None
    mouse_move_timeout = 0
    start_mouse_move_timeout = False
    escaped = False
    paused_by_esc = False
    track_paused = None
    replay = False
    bg_color = colors.hex_to_rgb(
        color_palette["CTk"]["fg_color"][0 if settings_json["appearance_mode"] == "Light" else 1])
    current_progressbar_width = 0
    replays = 0
    watchStart = 0
    watchEnd = 0
    voteStart = 0
    global_volume_modifier = settings_json["master_volume"]
    track_volume_modifier = settings_json["track_volume"] * (global_volume_modifier / 100) / 100
    gui_volume_modifier = settings_json["gui_volume"] * (global_volume_modifier / 100) / 100
    effects_volume_modifier = settings_json["effects_volume"] * (global_volume_modifier / 100) / 100
    add_new_date = True
    current_date = time.localtime()
    current_date = current_date.tm_mday, current_date.tm_mon, current_date.tm_year
    dates_used = data.get_value("dates_used")
    if dates_used:
        last_used_date = dates_used[-1]
        if last_used_date == list(current_date):
            add_new_date = False
    save_log("initialized variables")
    save_log("starting startup animation")
    settings_window, frame = settings.open_settings()
    settings_window.attributes("-alpha", 1)
    pygame.event.set_grab(True)
    pygame.event.set_grab(False)
    while running:
        pg.fill(bg_color)
        width, height = pg.get_size()

        # start up animation
        if intro:
            text = note_font.render("Press SPACE to skip the intro." if not lang else lang["startup"]["skip"], True,
                                    (50, 50, 50))
            pg.blit(text, (width // 2 - text.get_width() // 2, height - text.get_height() * 3))
            animation_state += 1
            pg.blit(icon_white, (width // 2 - icon_white_width_half, height // 2 - icon_white_height_half))
            glow_range = 60
            vibration = (math.sin(animation_state * 0.03) + 1) / 2
            current_alpha = 10 + (vibration * glow_range)
            icon_glow.set_alpha(current_alpha)
            pg.blit(icon_glow, (width // 2 - icon_glow_width_half, height // 2 - icon_glow_height_half))
            pygame.draw.rect(pg, bg_color, (width // 2 - icon_white_width_half, y_intro, icon_white_width_half * 2,
                                            icon_white_height_half * 2))
            if animation_state > 50:
                text = main_font.render("Song Comparator"[:(animation_state - 50) // 10], True, (255, 255, 255))
                text.set_alpha(animation_state + 50)
                pg.blit(text, (width // 2 - text.get_width() // 2, height // 2 + icon_white.get_height() // 2))
            y_intro -= 2
            if y_intro < init_y_intro - icon_white_height * 2:
                fade_surface = pygame.Surface((width, height))
                for x in range(75):
                    fade_surface.set_alpha(x)
                    fade_surface.fill((0, 0, 0))
                    pg.blit(fade_surface, (0, 0))
                    pygame.display.update()
                    pygame.time.delay(17)
                intro = False
                save_log("finished startup animation")
                save_log("adding values to data")
                data.add_value("session_count", 1)
                if add_new_date:
                    data.add_value_to_list("dates_used", current_date)
                save_log("finished adding values to data")
                save_log("start fade-in animation")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        fade_surface = pygame.Surface((width, height))
                        fade_surface.set_alpha(255)
                        fade_surface.fill((0, 0, 0))
                        pg.blit(fade_surface, (0, 0))
                        intro = False
                        save_log("skipping startup animation")
                        save_log("adding values to data")
                        data.add_value("session_count", 1)
                        if add_new_date:
                            data.add_value_to_list("dates_used", current_date)
                        save_log("finished adding values to data")
                        save_log("start fade-in animation")

        # main app
        else:
            # update the settings window if possible
            if settings_window:
                try:
                    settings_window.update()
                except tkinter.TclError:
                    settings_window = None
            id, text, bdetails = manager.draw_and_handle(pg, mouse_1_up)
            if text:
                save_log(f"clicked text: {text}, id: {id}")
                manager.disable_all()
                if id == "menu":
                    manager.clear()
                    if text == ("Playlist" if not lang else lang["program"]["playlist"]):
                        if len(data.listPlaylistFolder()) > 1:
                            for playlist in data.listPlaylistFolder():
                                manager.add_button(data.removeExtension(playlist), "playlist",
                                                   details=data.readPlaylist(playlist), base_color=base_color,
                                                   hover_color=hover_color, click_color=click_color,
                                                   disabled_color=disabled_color)
                            manager.layout(center_x=full_screen_viewport.centerx, center_y=full_screen_viewport.centery,
                                           max_width=full_screen_viewport.w)
                            currentMenu = "playlistSelection"
                        else:
                            randomPlaylist = data.randomPlaylist()
                            playlist = data.readPlaylist(randomPlaylist)
                            track = playlist[0]["track"]
                            isVideo = playlist[0].get("isVideo", True)
                            isStream = True if playlist[0].get("url") else False
                            coverIndex = 0
                            wasSingleTrack = False
                    elif text == ("Track" if not lang else lang["program"]["track"]):
                        if len(data.listTrackFolder()) > 1:
                            for iterated_track in data.listTrackFolder():
                                trackDetails = data.details(iterated_track, True, True)
                                manager.add_button(
                                    data.displayName(trackDetails) or data.removeExtension(
                                        iterated_track),
                                    "track", details=trackDetails, base_color=base_color, hover_color=hover_color,
                                    click_color=click_color, disabled_color=disabled_color)
                                manager.layout(center_x=full_screen_viewport.centerx,
                                               center_y=full_screen_viewport.centery,
                                               max_width=full_screen_viewport.w)
                            currentMenu = "trackSelection"
                        else:
                            wasSingleTrack = True
                            tracks = data.listTrackFolder()
                            if len(tracks) == 1:
                                track = tracks[0]
                            """Smartly set isStream in the future"""
                            isStream = False
                            isVideo = True if track.endswith(
                                (".mp4", ".webm", ".mov", ".avi", ".mkv", ".flv", ".m4v")) or isStream else False
                            currentMenu = "watching"
                            watchStart = time.time()
                elif id == "playlist":
                    playlist = bdetails
                    track = playlist[0]["track"]
                    isVideo = playlist[0].get("isVideo", True)
                    isStream = True if playlist[0].get("url") else False
                    coverIndex = 0
                    wasSingleTrack = False
                elif id == "track":
                    trackDetails = bdetails
                    track = trackDetails["track"]
                    isVideo = trackDetails.get("isVideo", True)
                    isStream = True if trackDetails.get("url") else False
                    wasSingleTrack = True
                else:
                    save_log(f"Unknown button text pressed: {text}, id: {id}", "warning")

            # handle events
            mouse_1_up = False
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                manager.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RETURN:
                        escaped = True
                    # track key controls
                    if video:
                        if event.key == pygame.K_j:
                            video.seek(-10)
                            save_log("seeking back 10 seconds in video mode")
                        elif event.key == pygame.K_k or event.key == pygame.K_SPACE:
                            video.toggle_pause()
                            if video.paused:
                                track_paused = True
                            else:
                                track_paused = False
                            save_log(f"toggled pause in video mode to: {video.paused} through keyboard")
                        elif event.key == pygame.K_LEFT:
                            video.seek(-5)
                            save_log("seeking back 5 seconds in video mode")
                        elif event.key == pygame.K_UP:
                            video.set_volume(video.get_volume() + 0.1)
                            save_log(f"adjusted volume in video mode to {video.get_volume()}")
                        elif event.key == pygame.K_DOWN:
                            video.set_volume(max(0.1, video.get_volume() - 0.1))
                            save_log(f"adjusted volume in video mode to {video.get_volume()}")
                    elif coverActive:
                        if event.key == pygame.K_j:
                            current_pos = pygame.mixer.music.get_pos()
                            new_pos = max(0, current_pos - 10000)
                            pygame.mixer.music.set_pos(new_pos / 1000)
                            save_log(f"seeking back 10 seconds in cover mode")
                        elif event.key == pygame.K_k or event.key == pygame.K_SPACE:
                            if pygame.mixer.music.get_busy():
                                pygame.mixer.music.pause()
                                track_paused = True
                            else:
                                pygame.mixer.music.unpause()
                                track_paused = False
                            save_log(
                                f"toggled pause in cover mode to: {not pygame.mixer.music.get_busy()} through keyboard")
                        elif event.key == pygame.K_LEFT:
                            current_pos = pygame.mixer.music.get_pos()
                            new_pos = max(0, current_pos - 5000)
                            pygame.mixer.music.set_pos(new_pos / 1000)
                            save_log(f"seeking back 5 seconds in cover mode")
                        elif event.key == pygame.K_UP:
                            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.1)
                            save_log(f"adjusted volume in cover mode to {video.get_volume()}")
                        elif event.key == pygame.K_DOWN:
                            pygame.mixer.music.set_volume(max(0.1, pygame.mixer.music.get_volume() - 0.1))
                            save_log(f"adjusted volume in cover mode to {video.get_volume()}")
                # track mouse controls
                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_pos = pygame.mouse.get_pos()
                    mouse_over_any_button = (
                            manager.is_mouse_over_any_button(mouse_pos) or
                            manager3.is_mouse_over_any_button(mouse_pos) or
                            (escaped or manager2.is_mouse_over_any_button(mouse_pos)))
                    if event.button == 1:
                        mouse_1_up = True
                        if not text and not mouse_over_any_button:
                            if video:
                                video.toggle_pause()
                                if video.paused:
                                    track_paused = True
                                else:
                                    track_paused = False
                                save_log(f"toggled pause in video mode to: {video.get_paused()} through mouse")
                            elif coverActive:
                                if pygame.mixer.music.get_busy():
                                    pygame.mixer.music.pause()
                                    track_paused = True
                                else:
                                    pygame.mixer.music.unpause()
                                    track_paused = False
                                save_log(
                                    f"toggled pause in cover mode to: {not pygame.mixer.music.get_busy()} through mouse")
                # video progressbar
                elif event.type == pygame.MOUSEMOTION:
                    if currentMenu == "watching":
                        start_mouse_move_timeout = True
                        save_log("mouse moved while watching")
                temp = False
                if video:
                    if video.paused:
                        temp = True
                if currentMenu == "watching" and (not pygame.mixer.music.get_busy() or temp):
                    start_mouse_move_timeout = True

                for widget in rating_widgets:
                    last_rect = widget.handle_event(event)

            # draw video under the escape bar
            if video:
                if video.active:
                    video.draw(pg, (0, 0))
                    if video.frame == video.frame_count:
                        currentMenu = "voting"
                        watchEnd = time.time()
                        voteStart = watchEnd
                        rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)
            elif coverActive and currentMenu == "watching":
                pg.blit(scaledCover, coverRect)
                current_pos = pygame.mixer.music.get_pos()
                track_length = data.get_track_length(track)
                if current_pos >= track_length - 50:
                    currentMenu = "voting"
                    watchEnd = time.time()
                    voteStart = watchEnd
                    rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)

            # video overlay
            if video:
                current_second = video.get_pos()
                total_seconds = video.frame_count / video.frame_rate
                progressbar_width_goal = width * video.frame / video.frame_count
                progressbar_with_difference = progressbar_width_goal - current_progressbar_width
                current_progressbar_width += progressbar_with_difference * 0.05
            elif coverActive:
                current_second = pygame.mixer.music.get_pos()
                total_seconds = data.get_track_length(track)
                progressbar_width_goal = width * current_second / total_seconds
                progressbar_with_difference = progressbar_width_goal - current_progressbar_width
                current_progressbar_width += progressbar_with_difference * 0.05
            if mouse_move_timeout > 0 and currentMenu == "watching" and not start_mouse_move_timeout:
                mouse_move_timeout -= 12
            if mouse_move_timeout > 0 and currentMenu == "watching":
                if not pygame.mouse.get_visible():
                    pygame.mouse.set_visible(True)
                    save_log("showing mouse")
                if video:
                    video_progressbar_fg = pygame.Surface((int(current_progressbar_width), 10))
                elif coverActive:
                    video_progressbar_fg = pygame.Surface((int(current_progressbar_width), 10))
                    current_second = current_second / 1000
                    total_seconds = total_seconds / 1000
                video_progressbar_bg = pygame.Surface((width - video_progressbar_fg.get_width(), 10))
                video_progressbar_bg.fill((111, 105, 157))
                video_progressbar_fg.fill((51, 45, 97))
                video_progressbar_bg.set_alpha(mouse_move_timeout)
                video_progressbar_fg.set_alpha(mouse_move_timeout)
                if track_data.__contains__("pre_notes"):
                    notes = track_data["pre_notes"]
                    for x, line in enumerate(reversed(notes)):
                        text = main_font.render(str(line), True, (255, 255, 255))
                        text.set_alpha(mouse_move_timeout)
                        pg.blit(text, (15, height - 15 - (x + 1) * text.get_height()))
                pg.blit(video_progressbar_bg, (video_progressbar_fg.get_width(), 0))
                pg.blit(video_progressbar_fg, (0, 0))
                text = main_font.render(str(round(current_second)), True, (255, 255, 255))
                text.set_alpha(mouse_move_timeout)
                pg.blit(text, (15, 15))
                text = main_font.render(str(round(total_seconds)), True, (255, 255, 255))
                text.set_alpha(mouse_move_timeout)
                pg.blit(text, (width - text.get_width() - 15, 15))
                text = main_font.render(f"{track_data["title"]} - {track_data["artist"]}", True, (255, 255, 255))
                text.set_alpha(mouse_move_timeout)
                pg.blit(text, (width / 2 - text.get_width() / 2, 15))
                cog_button.set_alpha(mouse_move_timeout)
            else:
                if currentMenu == "watching" and pygame.mouse.get_visible():
                    pygame.mouse.set_visible(False)
                    save_log("hiding mouse")
            if start_mouse_move_timeout or track_paused:
                start_mouse_move_timeout = True
                mouse_move_timeout += 12
                if mouse_move_timeout >= 2400:
                    start_mouse_move_timeout = False
                    mouse_move_timeout = 2400
            if currentMenu != "watching" and not pygame.mouse.get_visible():
                mouse_move_timeout = 0
                cog_button.reset_alpha()
                pygame.mouse.set_visible(True)
                save_log("showing mouse")

            # main menu logic
            if currentMenu == "main":
                manager.clear()
                manager.set_viewport(full_screen_viewport)
                manager.add_button("Playlist" if not lang else lang["program"]["playlist"], "menu",
                                   base_color=base_color, hover_color=hover_color, click_color=click_color,
                                   disabled_color=disabled_color)
                manager.add_button("Track" if not lang else lang["program"]["track"], "menu", base_color=base_color,
                                   hover_color=hover_color, click_color=click_color, disabled_color=disabled_color)
                manager.layout(center_x=full_screen_viewport.centerx, center_y=full_screen_viewport.centery,
                               max_width=full_screen_viewport.w)
                if len(data.listPlaylistFolder()) < 1:
                    manager.set_enabled("Playlist" if not lang else lang["program"]["playlist"], False)
                if len(data.listTrackFolder()) < 1:
                    manager.set_enabled("Track" if not lang else lang["program"]["track"], False)

            # voting menu logic
            if currentMenu == "voting":
                ratings = visuals.show_voting_screen(pg, rating_widgets)
                if track_data.__contains__("after_notes"):
                    notes = track_data["after_notes"]
                    for x, line in enumerate(notes):
                        text = main_font.render(str(line), True, (255, 255, 255))
                        pg.blit(text, (manager4.x + 30, 15 + x * text.get_height()))
                id, text, bdetails = manager4.draw_and_handle(pg, mouse_1_up)
                if text:
                    save_log(f"clicked text: {text}, id: {id}")
                    if id == "menu":
                        if text == "✅":
                            save_log(f"saving votings")
                            if not ratings.__contains__(0):
                                playedSongOnce = False
                                timeDiff = watchEnd - watchStart
                                total_listened_seconds = timeDiff + (total_listened_seconds := 0)
                                timeDiff = time.time() - voteStart
                                total_voted_seconds = timeDiff + (total_voted_seconds := 0)
                                data.saveTrackVoting(ratings=ratings, trackData=track_data, timeListening=total_listened_seconds, replays=replays, trackLength=data.get_track_length(track), timeVoting=total_voted_seconds)
                                save_log(f"saved votings")
                                save_log(f"resetting track")
                                if wasSingleTrack:
                                    track = None
                                    video = None
                                    currentMenu = "main"
                                else:
                                    video = None
                                    try:
                                        for x, i in enumerate(playlist):
                                            if track == i["track"]:
                                                track = playlist[x + 1]["track"]
                                                coverIndex = x + 1
                                                break
                                    except IndexError:
                                        track = None
                                        video = None
                                        currentMenu = "main"
                                save_log(f"finished resetting track")
                        elif text == "🔁":
                            timeDiff = watchEnd - watchStart
                            total_listened_seconds = timeDiff + (total_listened_seconds := 0)
                            timeDiff = time.time() - voteStart
                            total_voted_seconds = timeDiff + (total_voted_seconds := 0)
                            replay = True
                            replays += 1
                        else:
                            save_log(f"Unknown button text pressed: {text}, id: {id}", "warning")
                manager4.clear()
                manager4.add_button("🔁", "menu", base_color=base_color,
                                    hover_color=hover_color, click_color=click_color, disabled_color=disabled_color)
                submit_button = manager4.add_button("✅", "menu",
                                                    base_color=base_color, hover_color=hover_color,
                                                    click_color=click_color,
                                                    disabled_color=disabled_color)
                space_rect_border_v = width - last_rect.x - last_rect.width
                space_rect_border_h = height - (last_rect.y + last_rect.height)
                voting_viewport = pygame.Rect(width - space_rect_border_v,
                                              height - space_rect_border_h - submit_button.h,
                                              space_rect_border_v, submit_button.h)
                manager4.set_viewport(voting_viewport)
                manager4.layout(center_x=voting_viewport.centerx, center_y=voting_viewport.centery,
                                max_width=voting_viewport.w)
                if ratings.__contains__(0):
                    text = ntri_font.render("Please rate the song." if not lang else lang["voting"]["rate_song_info"],
                                            True, (155, 50, 50))
                    pg.blit(text, (submit_button.x + (submit_button.w // 2) - text.get_width() // 2 + manager4.x,
                                   height - (height - (
                                           manager4.y + submit_button.y + submit_button.h)) + text.get_height() // 2))
                    manager4.set_enabled("✅", False)
                else:
                    manager4.set_enabled("✅")
            # sets the next video or cover
            if (not video and track and not playedSongOnce) or replay:
                save_log("setting up next video or cover")
                track_data = data.details(track, True, True)
                if not replay:
                    replays = 0
                replay = False
                currentMenu = "watching"
                watchStart = time.time()
                manager.clear()
                if isVideo:
                    if not video or not video.active:
                        coverActive = False
                        if isStream:
                            video = pyvidplayer2.Video(track, youtube=True)
                        else:
                            video = pyvidplayer2.Video(data.trackfolder + track, youtube=False)
                        video.resize((width, height))
                        video.set_volume(track_volume_modifier)
                        save_log("finished setting up video")
                else:
                    current_pos = pygame.mixer.music.get_pos()
                    track_length = data.get_track_length(track)
                    if ((current_pos <= track_length - 50) and not playedSongOnce and not currentMenu == "voting"
                            and playlist and coverIndex):
                        pygame.mixer.music.load(data.trackfolder + track)
                        pygame.mixer.music.set_volume(track_volume_modifier)
                        pygame.mixer.music.play()
                        coverActive = True
                        cover = playlist[coverIndex]["cover"]
                        scaledCover, coverRect = visuals.calc_cover(cover, width, height)
                        playedSongOnce = True
                        save_log("finished setting up cover type: 1")
                    else:
                        pygame.mixer.music.load(data.trackfolder + track)
                        pygame.mixer.music.set_volume(track_volume_modifier)
                        pygame.mixer.music.play()
                        coverActive = True
                        details = data.details(track, True, True)
                        if "cover" in details and details["cover"]:
                            if os.path.exists(f"{data.coverfolder}{details["cover"]}"):
                                coverFound = True
                                cover = details["cover"]
                            else:
                                coverFound = False
                                cover = None
                        else:
                            coverFound = False
                            cover = None
                        scaledCover, coverRect = visuals.calc_cover(cover, width, height, coverFound)
                        playedSongOnce = True
                        save_log("finished setting up cover type: 2")
            if currentMenu == "main" or mouse_move_timeout > 0:
                manager3.set_viewport(title_button_viewport)
                manager3.layout(center_x=title_button_viewport.centerx, center_y=title_button_viewport.centery,
                                max_width=title_button_viewport.w)
                id, text, bdetails = manager3.draw_and_handle(pg, mouse_1_up)
                if id == "menu":
                    save_log(f"clicked text: {text}, id: {id}")
                    if text == "⚙️":
                        escaped = True
                        manager3.set_enabled("⚙️", False)
                    else:
                        save_log(f"Unknown button text pressed: {text}, id: {id}", "warning")
            if escaped:
                if video or coverActive:
                    if not track_paused:
                        paused_by_esc = True
                        if video:
                            video.pause()
                        elif coverActive:
                            pygame.mixer.music.pause()
                        track_paused = True
                esc_menu = pygame.Surface((width, height))
                esc_menu.set_alpha(200)
                esc_menu.fill((0, 0, 0))
                pg.blit(esc_menu, (0, 0))
                manager.set_enabled("Playlist" if not lang else lang["program"]["playlist"], False)
                manager.set_enabled("Track" if not lang else lang["program"]["track"], False)
                manager2.clear()
                manager2.add_button("Back", "esc_menu", base_color=base_color, hover_color=hover_color,
                                    click_color=click_color, disabled_color=disabled_color)
                manager2.add_button("Settings", "esc_menu", base_color=base_color, hover_color=hover_color,
                                    click_color=click_color, disabled_color=disabled_color)
                manager2.add_button("Calculate Data", "esc_menu", base_color=base_color, hover_color=hover_color,
                                    click_color=click_color, disabled_color=disabled_color)
                manager2.set_viewport(title_viewport)
                manager2.layout(center_x=title_viewport.centerx, center_y=title_viewport.centery,
                                max_width=title_viewport.w)
                id, text, bdetails = manager2.draw_and_handle(pg, mouse_1_up)
                if id == "esc_menu":
                    save_log(f"clicked text: {text}, id: {id}")
                    if text == "Back":
                        escaped = False
                        manager3.set_enabled("⚙️")
                    elif text == "Settings":
                        if settings_window:
                            settings_window.deiconify()
                            settings_window.focus()
                            frame._parent_canvas.yview_moveto(0)
                    elif text == "Calculate Data":
                        tkinter.messagebox.showinfo("Calculate Data", "This feature is not yet implemented")
                    else:
                        save_log(f"Unknown button text pressed: {text}, id: {id}", "warning")
            else:
                if paused_by_esc:
                    if video:
                        video.resume()
                        save_log("unpaused video by escape")
                    elif coverActive:
                        pygame.mixer.music.unpause()
                        save_log("unpaused cover by escape")
                    paused_by_esc = False
                    track_paused = False

            # quit app logic
            if keys[pygame.K_ESCAPE]:
                save_log("pressing escape")
                esc += 1
                pg.fill((255, 0, 0), (0, height - 50, width // 200 * esc, 50))
            else:
                esc = 0
            if esc == 215:
                running = False
                save_log("closing app through escape")
            # intro fade-in
            if fadein < 255:
                fade_surface = pygame.Surface((width, height))
                fade_surface.set_alpha(255 - fadein)
                fade_surface.fill((0, 0, 0))
                pg.blit(fade_surface, (0, 0))
                pygame.display.update()
                pygame.time.delay(17)
                fadein += 3
                if fadein == 255:
                    save_log("finished fade-in animation")
        pygame.display.update()
        clock.tick(120)
    pygame.quit()


if __name__ == "__main__":
    run()
