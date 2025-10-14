import os

import pygame
import pyvidplayer2

import data
import misc
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
    video = None
    coverActive = False
    font = pygame.font.SysFont("Segoe UI", 48)
    manager = visuals.ButtonManager(font)
    manager.add_button("Playlist" if not lang else lang["program"]["playlist"])
    manager.add_button("Track" if not lang else lang["program"]["track"])
    viewport = pygame.Rect(0, 0, width, height)  # full-screen viewport
    manager.set_viewport(viewport)
    manager.layout(center_x=viewport.centerx, center_y=viewport.centery, max_width=viewport.w)
    icon_white = pygame.image.load("resources/assets/icon_white.png")
    icon_white = pygame.transform.smoothscale_by(icon_white, 3)
    icon_white = pygame.transform.smoothscale(icon_white, (icon_white.get_width() // 4, icon_white.get_height() // 4))
    icon_white_height = icon_white.get_height()
    icon_white_width_half = icon_white.get_width() // 2
    icon_white_height_half = icon_white.get_height() // 2
    currentMenu = "main"
    intro = False  # reset to True when finished
    fadein = 255  # reset to 0 when finished
    y_intro = height // 2 - icon_white_height_half
    init_y_intro = y_intro
    main_font = pygame.font.SysFont("Segoe UI", 42, True)
    rating_widgets = visuals.setup_voting_widgets(width, height, main_font, lang)
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
            clicks = manager.draw_and_handle(pg)
            for c in clicks:
                manager.disable_all()
                if currentMenu == "main":
                    manager.clear()
                    if c == ("Playlist" if not lang else lang["program"]["playlist"]):
                        if len(os.listdir("resources/playlists")) > 1:
                            for playlist in os.listdir("resources/playlists"):
                                manager.add_button(data.removeExtension(playlist))
                                manager.layout(center_x=viewport.centerx, center_y=viewport.centery,
                                               max_width=viewport.w)
                                currentMenu = "playlistSelection"
                        else:
                            randomPlaylist = data.randomPlaylist()
                            playlist = data.readPlaylist(randomPlaylist)
                            randomTrack = data.randomTrack(playlist)
                            source, stream, isVideo = data.trackSource(randomTrack)
                            pygame.mixer.music.stop()
                            if video:
                                video.stop()
                                video = None
                            if isVideo:
                                coverActive = False
                                video = pyvidplayer2.Video(source, youtube=stream)
                                video.resize((width, height))
                            else:
                                pygame.mixer.music.load(source)
                                coverActive = True
                                scaledCover, cover_rect = visuals.calc_cover(randomTrack, width, height)
                                pg.fill((0, 0, 0))
                                pg.blit(scaledCover, cover_rect)
                                pygame.mixer.music.play()
                    elif c == ("Track" if not lang else lang["program"]["track"]):
                        if len(os.listdir("resources/tracks")) > 1:
                            for track in os.listdir("resources/tracks"):
                                manager.add_button(
                                    data.displayName(data.details(track, True, True)) or data.removeExtension(track))
                                manager.layout(center_x=viewport.centerx, center_y=viewport.centery,
                                               max_width=viewport.w)
                                currentMenu = "trackSelection"
                        else:
                            video = pyvidplayer2.Video("resources/tracks/Aber sie.mp4")
                            print(video)
                elif currentMenu == "playlistSelection":
                    pass
                    # play the selected playlist
                elif currentMenu == "trackSelection":
                    pass
                    # play the selected track
                elif currentMenu == "voting":
                    if c == ("Submit" if not lang else lang["voting"]["submit"]):
                        data.save_voting(ratings, title="")
                else:
                    print(f"{c} pressed")

            # handle events
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                manager.handle_event(event)
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYUP:
                    if video:
                        if event.key == pygame.K_j:
                            video.seek(-10)
                        elif event.key == pygame.K_k:
                            video.toggle_pause()
                        elif event.key == pygame.K_l:
                            video.seek(10)
                        elif event.key == pygame.K_SPACE:
                            video.toggle_pause()
                        elif event.key == pygame.K_LEFT:
                            video.seek(-5)
                        elif event.key == pygame.K_UP:
                            video.set_volume(video.get_volume() + 0.1)
                        elif event.key == pygame.K_DOWN:
                            video.set_volume(video.get_volume() - 0.1)
                        elif event.key == pygame.K_RIGHT:
                            video.seek(5)
                if pygame.mouse.get_pressed()[0]:
                    if video:
                        video.toggle_pause()
                for widget in rating_widgets:
                    last_rect = widget.handle_event(event)

            # draw video under the escape bar
            if video:
                video.draw(pg, (0, 0))

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

            # main menu logic
            if currentMenu == "main":
                if len(os.listdir("resources/playlists")) < 1:
                    manager.set_enabled("Playlist" if not lang else lang["program"]["playlist"], False)
                if len(os.listdir("resources/tracks")) < 1:
                    manager.set_enabled("Track" if not lang else lang["program"]["track"], False)

            # voting menu logic
            if currentMenu == "voting":
                manager.clear()
                button = manager.add_button("Submit" if not lang else lang["voting"]["submit"])
                space_rect_border_v = width - last_rect.x - last_rect.width
                space_rect_border_h = height - (last_rect.y + last_rect.height)
                viewport = pygame.Rect(width - space_rect_border_v, height - space_rect_border_h - button.h,
                                       space_rect_border_v, button.h)
                manager.set_viewport(viewport)
                manager.layout(center_x=viewport.centerx, center_y=viewport.centery, max_width=viewport.w)
                ratings = visuals.show_voting_screen(pg, rating_widgets)
        pygame.display.update()
        clock.tick(120)
    pygame.quit()


if __name__ == "__main__":
    run()
