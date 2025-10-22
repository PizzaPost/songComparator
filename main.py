import os
import tkinter

import pygame
import pyvidplayer2

import data
import misc
import settings
import visuals


def run():
    lang = misc.load_language()
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
    font = pygame.font.SysFont("Segoe UI", 48)
    emojiFont = pygame.font.SysFont("segoeuiemoji", 48)
    manager = visuals.ButtonManager(font)
    manager2 = visuals.ButtonManager(font)
    manager3 = visuals.ButtonManager(emojiFont)
    manager3.add_button("⚙️", "menu")
    full_screen_viewport = pygame.Rect(0, 0, width, height)
    title_button_viewport = pygame.Rect(width - 200, height - 200, 200, 200)
    title_viewport = pygame.Rect(0, 100, width, height - 100)
    icon_white = pygame.image.load("resources/assets/icon_white.png")
    icon_white = pygame.transform.smoothscale_by(icon_white, 3)
    icon_white = pygame.transform.smoothscale(icon_white, (icon_white.get_width() // 4, icon_white.get_height() // 4))
    icon_white_height = icon_white.get_height()
    icon_white_width_half = icon_white.get_width() // 2
    icon_white_height_half = icon_white.get_height() // 2
    currentMenu = "main"
    intro = False  # reset to True when finished coding
    fadein = 255  # reset to 0 when finished coding
    y_intro = height // 2 - icon_white_height_half
    init_y_intro = y_intro
    main_font = pygame.font.SysFont("Segoe UI", 42, True)
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
    while running:
        pg.fill((0, 0, 0))
        width, height = pg.get_size()

        # start up animation
        if intro:
            pg.blit(icon_white, (width // 2 - icon_white_width_half, height // 2 - icon_white_height_half))
            pygame.draw.rect(pg, (0, 0, 0), (width // 2 - icon_white_width_half, y_intro, icon_white_width_half * 2,
                                             icon_white_height_half * 2))
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

        # main app
        else:
            # update the settings window if possible
            if settings_window:
                try:
                    settings_window.update()
                except tkinter.TclError:
                    settings_window = None
            id, text = manager.draw_and_handle(pg, mouse_1_up)
            if text:
                manager.disable_all()
                if id == "menu":
                    manager.clear()
                    if text == ("Playlist" if not lang else lang["program"]["playlist"]):
                        if len(os.listdir("resources/playlists")) > 1:
                            for playlist in os.listdir("resources/playlists"):
                                manager.add_button(data.removeExtension(playlist), "playlist")
                            manager.layout(center_x=full_screen_viewport.centerx, center_y=full_screen_viewport.centery,
                                           max_width=full_screen_viewport.w)
                            currentMenu = "playlistSelection"
                        else:
                            randomPlaylist = data.randomPlaylist()
                            playlist = data.readPlaylist(randomPlaylist)
                            track = playlist[0]["track"]
                            isVideo = playlist[0].get("isVideo", True)
                            isStream = playlist[0].get("isStream", False)
                            coverIndex = 0
                            wasSingleTrack = False
                    elif text == ("Track" if not lang else lang["program"]["track"]):
                        if len(os.listdir("resources/tracks")) > 1:
                            for iterated_track in os.listdir("resources/tracks"):
                                manager.add_button(
                                    data.displayName(data.details(iterated_track, True, True)) or data.removeExtension(
                                        iterated_track),
                                    "track")
                                manager.layout(center_x=full_screen_viewport.centerx,
                                               center_y=full_screen_viewport.centery,
                                               max_width=full_screen_viewport.w)
                            currentMenu = "trackSelection"
                        else:
                            wasSingleTrack = True
                            tracks = os.listdir("resources/tracks")
                            if len(tracks) == 1:
                                track = tracks[0]
                            """Smartly set isStream in the future"""
                            isStream = False
                            isVideo = True if track.endswith(
                                (".mp4", ".webm", ".mov", ".avi", ".mkv", ".flv", ".m4v")) or isStream else False
                            currentMenu = "watching"
                    if text == ("Submit" if not lang else lang["voting"]["submit"]):
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

                        title = None  # dummy code
                        data.save_voting(ratings, title)
                elif id == "playlist":
                    pass
                    # play the selected playlist
                elif id == "track":
                    pass
                    # play the selected track
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
                            if track.paused:
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
                            (escaped or manager2.is_mouse_over_any_button(mouse_pos))
                    )
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
                video_progressbar_bg = pygame.Surface((width, 10))
                if video:
                    video_progressbar_fg = pygame.Surface((int(width * video.frame / video.frame_count), 10))
                elif coverActive:
                    video_progressbar_fg = pygame.Surface(
                        (int(width * pygame.mixer.music.get_pos() / data.get_track_length(track)), 10))
                video_progressbar_bg.fill((111, 105, 157))
                video_progressbar_fg.set_alpha(mouse_move_timeout)
                video_progressbar_fg.fill((51, 45, 97))
                # FUTURE:
                # current second
                # duration
                # display the title
                # display the artist
                # display extra notes
                # queue
                pg.blit(video_progressbar_bg, (0, 0))
                pg.blit(video_progressbar_fg, (0, 0))
            if start_mouse_move_timeout:
                mouse_move_timeout += 12
                if mouse_move_timeout >= 2400:
                    start_mouse_move_timeout = False
                    mouse_move_timeout = 2400

            # intro fade-in
            if fadein < 255:
                fade_surface = pygame.Surface((width, height))
                fade_surface.set_alpha(255 - fadein)
                fade_surface.fill((0, 0, 0))
                pg.blit(fade_surface, (0, 0))
                pygame.display.update()
                pygame.time.delay(17)
                fadein += 3

            # main menu logic
            if currentMenu == "main":
                manager.clear()
                manager.set_viewport(full_screen_viewport)
                manager.add_button("Playlist" if not lang else lang["program"]["playlist"], "menu")
                manager.add_button("Track" if not lang else lang["program"]["track"], "menu")
                manager.layout(center_x=full_screen_viewport.centerx, center_y=full_screen_viewport.centery,
                               max_width=full_screen_viewport.w)
                if len(os.listdir("resources/playlists")) < 1:
                    manager.set_enabled("Playlist" if not lang else lang["program"]["playlist"], False)
                if len(os.listdir("resources/tracks")) < 1:
                    manager.set_enabled("Track" if not lang else lang["program"]["track"], False)

            # voting menu logic
            if currentMenu == "voting":
                manager.clear()
                button = manager.add_button("Submit" if not lang else lang["voting"]["submit"], "menu")
                space_rect_border_v = width - last_rect.x - last_rect.width
                space_rect_border_h = height - (last_rect.y + last_rect.height)
                voting_viewport = pygame.Rect(width - space_rect_border_v, height - space_rect_border_h - button.h,
                                              space_rect_border_v, button.h)
                manager.set_viewport(voting_viewport)
                manager.layout(center_x=voting_viewport.centerx, center_y=voting_viewport.centery,
                               max_width=voting_viewport.w)
                ratings = visuals.show_voting_screen(pg, rating_widgets)

            # sets the next video or cover
            if not video and track and not playedSongOnce:
                currentMenu = "watching"
                manager.clear()
                if isVideo:
                    if not video:
                        coverActive = False
                        video = pyvidplayer2.Video("resources/tracks/" + track, youtube=isStream)
                        video.resize((width, height))
                    elif not video.active:
                        coverActive = False
                        video = pyvidplayer2.Video("resources/tracks/" + track, youtube=isStream)
                        video.resize((width, height))
                else:
                    current_pos = pygame.mixer.music.get_pos()
                    track_length = data.get_track_length(track)
                    if (
                            current_pos <= track_length - 50) and not playedSongOnce and not currentMenu == "voting" and playlist and coverIndex:
                        pygame.mixer.music.load("resources/tracks/" + track)
                        pygame.mixer.music.play()
                        coverActive = True
                        cover = playlist[coverIndex]["cover"]
                        scaledCover, coverRect = visuals.calc_cover(cover, width, height)
                        playedSongOnce = True
                    else:
                        pygame.mixer.music.load("resources/tracks/" + track)
                        pygame.mixer.music.play()
                        coverActive = True
                        coverFound = False
                        for found_playlist in os.listdir("resources/playlists"):
                            with open(f"resources/playlists/{found_playlist}", "r") as f:
                                playlist_data = data.readPlaylist(found_playlist)
                            f.close()
                            for index, playlist_track in enumerate(playlist_data):
                                if playlist_track["track"] == data.removeExtension(track):
                                    cover = playlist_track["cover"]
                                    if os.path.exists(f"resources/covers/{cover}"):
                                        coverFound = True
                                        break
                            if coverFound:
                                break
                        if not coverFound:
                            cover = None
                            coverFound = False
                        scaledCover, coverRect = visuals.calc_cover(cover, width, height, coverFound)
                        playedSongOnce = True
            if currentMenu == "main" or mouse_move_timeout > 0:
                manager3.set_viewport(title_button_viewport)
                manager3.layout(center_x=title_button_viewport.centerx, center_y=title_button_viewport.centery,
                                max_width=title_button_viewport.w)
                id, text = manager3.draw_and_handle(pg, mouse_1_up)
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
                esc_menu = pygame.Surface((width, height))
                esc_menu.set_alpha(200)
                esc_menu.fill((0, 0, 0))
                pg.blit(esc_menu, (0, 0))
                manager.set_enabled("Playlist" if not lang else lang["program"]["playlist"], False)
                manager.set_enabled("Track" if not lang else lang["program"]["track"], False)
                manager2.clear()
                manager2.add_button("Back", "esc_menu")
                manager2.add_button("Settings", "esc_menu")
                manager2.add_button("Calculate Data", "esc_menu")
                manager2.set_viewport(title_viewport)
                manager2.layout(center_x=title_viewport.centerx, center_y=title_viewport.centery,
                                max_width=title_viewport.w)
                id, text = manager2.draw_and_handle(pg, mouse_1_up)
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

            # quit app logic
            if keys[pygame.K_ESCAPE]:
                esc += 1
                pg.fill((255, 0, 0), (0, height - 50, width // 200 * esc, 50))
            else:
                esc = 0
            if esc == 215:
                running = False
        pygame.display.update()
        clock.tick(120)
    pygame.quit()


if __name__ == "__main__":
    run()
