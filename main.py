import math
import os
import tkinter

import pygame
import pyvidplayer2

import colors
import data
import misc
import settings
import visuals


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
    icon_glow_height = icon_glow.get_height()
    icon_glow_width_half = icon_glow.get_width() // 2
    icon_glow_height_half = icon_glow.get_height() // 2
    currentMenu = "main"
    intro = True  # reset to True when finished coding
    fadein = 0  # reset to 0 when finished coding
    y_intro = height // 2 - icon_white_height_half
    init_y_intro = y_intro
    animation_state = 0
    main_font = pygame.font.Font(settings_json["font"], 42)
    rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)
    mouse_1_up = False
    wasSingleTrack = False
    playedSongOnce = False
    playlist = None
    coverIndex = None
    mouse_move_timeout = 0
    start_mouse_move_timeout = False
    escaped = False
    settings_window = None
    paused_by_esc = False
    track_paused = None
    replay = False
    bg_color = colors.hex_to_rgb(
        color_palette["CTk"]["fg_color"][0 if settings_json["appearance_mode"] == "Light" else 1])
    while running:
        pg.fill(bg_color)
        width, height = pg.get_size()

        # start up animation
        if intro:
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
                data.add_value("sessions", 1)

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
                    elif text == ("Submit" if not lang else lang["voting"]["submit"]):
                        playedSongOnce = False
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
                        # (if) search in playlists
                        '''if '''
                        """     Pls add your logic here"""
                        '''else:
                            title=data.removeExtension(track)'''

                        title = track  # dummy code
                        data.save_voting(ratings, title)
                    elif text == ("Replay" if not lang else lang["voting"]["replay"]):
                        replay = True
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
                    print(f"{text} pressed and could not be matched to any id.")

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
                        elif event.key == pygame.K_k or event.key == pygame.K_SPACE:
                            video.toggle_pause()
                            if video.paused:
                                track_paused = True
                            else:
                                track_paused = False
                        # I don't really know if it should be possible to skip forward
                        # elif event.key == pygame.K_l:
                        #     remaining_length = video.frame_count - video.frame
                        #     if video.duration > (video.frame / video.frame_count) * video.duration + 10:
                        #         seek_amount = min(10, remaining_length)
                        #         video.seek(seek_amount)
                        elif event.key == pygame.K_LEFT:
                            video.seek(-5)
                        elif event.key == pygame.K_UP:
                            video.set_volume(video.get_volume() + 0.1)
                        elif event.key == pygame.K_DOWN:
                            video.set_volume(max(0.1, video.get_volume() - 0.1))
                        # I don't really know if it should be possible to skip forward
                        # elif event.key == pygame.K_RIGHT:
                        #     remaining_length = video.frame_count - video.frame
                        #     if video.duration > (video.frame / video.frame_count) * video.duration + 5:
                        #         seek_amount = min(5, remaining_length)
                        #         video.seek(seek_amount)
                    elif coverActive:
                        if event.key == pygame.K_j:
                            current_pos = pygame.mixer.music.get_pos()
                            new_pos = max(0, current_pos - 10000)
                            pygame.mixer.music.set_pos(new_pos / 1000)
                        elif event.key == pygame.K_k or event.key == pygame.K_SPACE:
                            if pygame.mixer.music.get_busy():
                                pygame.mixer.music.pause()
                                track_paused = True
                            else:
                                pygame.mixer.music.unpause()
                                track_paused = False
                        # I don't really know if it should be possible to skip forward
                        # elif event.key == pygame.K_l:  # BUGGED!!!
                        #     current_pos = pygame.mixer.music.get_pos()
                        #     track_length = data.get_track_length(track)
                        #     new_pos = min(current_pos + 10000, track_length)
                        #     pygame.mixer.music.set_pos(new_pos / 1000)
                        elif event.key == pygame.K_LEFT:
                            current_pos = pygame.mixer.music.get_pos()
                            new_pos = max(0, current_pos - 5000)
                            pygame.mixer.music.set_pos(new_pos / 1000)
                        elif event.key == pygame.K_UP:
                            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.1)
                        elif event.key == pygame.K_DOWN:
                            pygame.mixer.music.set_volume(max(0.1, pygame.mixer.music.get_volume() - 0.1))
                        # I don't really know if it should be possible to skip forward
                        # elif event.key == pygame.K_RIGHT:  # BUGGED!!!
                        #     current_pos = pygame.mixer.music.get_pos()
                        #     track_length = data.get_track_length(track)
                        #     new_pos = min(current_pos + 5000, track_length)
                        #     pygame.mixer.music.set_pos(new_pos / 1000)"""
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
                            elif coverActive:
                                if pygame.mixer.music.get_busy():
                                    pygame.mixer.music.pause()
                                    track_paused = True
                                else:
                                    pygame.mixer.music.unpause()
                                    track_paused = False
                # video progressbar
                elif event.type == pygame.MOUSEMOTION:
                    if currentMenu == "watching":
                        start_mouse_move_timeout = True
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
                        rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)
            elif coverActive and currentMenu == "watching":
                pg.blit(scaledCover, coverRect)
                current_pos = pygame.mixer.music.get_pos()
                track_length = data.get_track_length(track)
                if current_pos >= track_length - 50:
                    currentMenu = "voting"
                    rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)

            # draw video progressbar
            if mouse_move_timeout > 0 and currentMenu == "watching" and not start_mouse_move_timeout:
                mouse_move_timeout -= 12
            if mouse_move_timeout > 0 and currentMenu == "watching":
                pygame.mouse.set_visible(True)
                if video:
                    current_second = video.get_pos()
                    total_seconds = video.frame_count / video.frame_rate
                    video_progressbar_fg = pygame.Surface((int(width * video.frame / video.frame_count), 10))
                elif coverActive:
                    current_second = pygame.mixer.music.get_pos()
                    total_seconds = data.get_track_length(track)
                    video_progressbar_fg = pygame.Surface(
                        (int(width * current_second / total_seconds), 10))
                    current_second = current_second / 1000
                    total_seconds = total_seconds / 1000
                video_progressbar_bg = pygame.Surface((width - video_progressbar_fg.get_width(), 10))
                video_progressbar_bg.fill((111, 105, 157))
                video_progressbar_fg.fill((51, 45, 97))
                video_progressbar_bg.set_alpha(mouse_move_timeout)
                video_progressbar_fg.set_alpha(mouse_move_timeout)
                # FUTURE:
                # display the artist
                # display extra notes
                # queue
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
                pygame.mouse.set_visible(False)
            if start_mouse_move_timeout or track_paused:
                start_mouse_move_timeout = True
                mouse_move_timeout += 12
                if mouse_move_timeout >= 2400:
                    start_mouse_move_timeout = False
                    mouse_move_timeout = 2400
            if currentMenu != "watching":
                mouse_move_timeout = 0
                cog_button.reset_alpha()
                pygame.mouse.set_visible(True)

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
                manager.clear()
                manager.add_button("Replay" if not lang else lang["voting"]["replay"], "menu", base_color=base_color,
                                   hover_color=hover_color, click_color=click_color, disabled_color=disabled_color)
                button = manager.add_button("Submit" if not lang else lang["voting"]["submit"], "menu",
                                            base_color=base_color, hover_color=hover_color, click_color=click_color,
                                            disabled_color=disabled_color)
                space_rect_border_v = width - last_rect.x - last_rect.width
                space_rect_border_h = height - (last_rect.y + last_rect.height)
                voting_viewport = pygame.Rect(width - space_rect_border_v, height - space_rect_border_h - button.h,
                                              space_rect_border_v, button.h)
                manager.set_viewport(voting_viewport)
                manager.layout(center_x=voting_viewport.centerx, center_y=voting_viewport.centery,
                               max_width=voting_viewport.w)
                ratings = visuals.show_voting_screen(pg, rating_widgets)

            # sets the next video or cover
            if (not video and track and not playedSongOnce) or replay:
                track_data = data.details(track, True, True)
                replay = False
                currentMenu = "watching"
                manager.clear()
                if isVideo:
                    if not video or not video.active:
                        coverActive = False
                        video = pyvidplayer2.Video(data.trackfolder + track, youtube=isStream)
                        video.resize((width, height))
                else:
                    current_pos = pygame.mixer.music.get_pos()
                    track_length = data.get_track_length(track)
                    if ((current_pos <= track_length - 50) and not playedSongOnce and not currentMenu == "voting"
                            and playlist and coverIndex):
                        pygame.mixer.music.load(data.trackfolder + track)
                        pygame.mixer.music.play()
                        coverActive = True
                        cover = playlist[coverIndex]["cover"]
                        scaledCover, coverRect = visuals.calc_cover(cover, width, height)
                        playedSongOnce = True
                    else:
                        pygame.mixer.music.load(data.trackfolder + track)
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
            if currentMenu == "main" or mouse_move_timeout > 0:
                manager3.set_viewport(title_button_viewport)
                manager3.layout(center_x=title_button_viewport.centerx, center_y=title_button_viewport.centery,
                                max_width=title_button_viewport.w)
                id, text, bdetails = manager3.draw_and_handle(pg, mouse_1_up)
                if id == "menu":
                    if text == "⚙️":
                        escaped = True
                        manager3.set_enabled("⚙️", False)
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
                    if text == "Back":
                        escaped = False
                        manager3.set_enabled("⚙️")
                    elif text == "Settings":
                        if settings_window is None:
                            settings_window, frame = settings.open_settings()
                        else:
                            settings_window.deiconify()
                            settings_window.focus()
                            frame._parent_canvas.yview_moveto(0)
                    elif text == "Calculate Data":
                        tkinter.messagebox.showinfo("Calculate Data", "This feature is not yet implemented")
            else:
                if paused_by_esc:
                    if video:
                        video.resume()
                    elif coverActive:
                        pygame.mixer.music.unpause()
                    paused_by_esc = False
                    track_paused = False

            # quit app logic
            if keys[pygame.K_ESCAPE]:
                esc += 1
                pg.fill((255, 0, 0), (0, height - 50, width // 200 * esc, 50))
            else:
                esc = 0
            if esc == 215:
                running = False
            # intro fade-in
            if fadein < 255:
                fade_surface = pygame.Surface((width, height))
                fade_surface.set_alpha(255 - fadein)
                fade_surface.fill((0, 0, 0))
                pg.blit(fade_surface, (0, 0))
                pygame.display.update()
                pygame.time.delay(17)
                fadein += 3
        pygame.display.update()
        clock.tick(120)
    pygame.quit()


if __name__ == "__main__":
    run()
