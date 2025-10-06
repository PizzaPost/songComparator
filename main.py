import os


def run():
    import pygame
    import pyvidplayer2
    import visuals
    import data
    import misc
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
    currentMenu="main"
    while running:
        if not coverActive:
            pg.fill((0, 0, 0))
        if currentMenu=="main":
            if len(os.listdir("resources/playlists")) < 1:
                manager.set_enabled("Playlist" if not lang else lang["program"]["playlist"], False)
            if len(os.listdir("resources/tracks")) < 1:
                manager.set_enabled("Track" if not lang else lang["program"]["track"], False)
        clicks = manager.draw_and_handle(pg)
        for c in clicks:
            manager.disable_all()
            if currentMenu=="main":
                manager.clear()
                if c == ("Playlist" if not lang else lang["program"]["playlist"]):
                    if len(os.listdir("resources/playlists"))>1:
                        for playlist in os.listdir("resources/playlists"):
                            manager.add_button(data.removeExtension(playlist))
                            manager.layout(center_x=viewport.centerx, center_y=viewport.centery, max_width=viewport.w)
                            currentMenu="playlistSelection"
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
                            manager.add_button(data.displayName(data.details(track, True, True)) or data.removeExtension(track))
                            manager.layout(center_x=viewport.centerx, center_y=viewport.centery, max_width=viewport.w)
                            currentMenu = "trackSelection"
            if currentMenu == "playlistSelection":
                pass
                # play the selected playlist
            elif currentMenu == "trackSelection":
                pass
                # play the selected track
            else:
                print(f"{c} pressed")

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            manager.handle_event(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    if video:
                        video.toggle_pause()
        if keys[pygame.K_l]:
            if video:
                video.seek(5)
        elif keys[pygame.K_j]:
            if video:
                video.seek(-5)
        if esc == 215:
            running = False
        if video:
            video.draw(pg, (0, 0))
        if keys[pygame.K_ESCAPE]:
            esc += 1
            pg.fill((255, 0, 0), (0, height - 50, width // 200 * esc, 50))
        else:
            esc = 0
        pygame.display.update()
        clock.tick(120)
    pygame.quit()


if __name__ == "__main__":
    run()
