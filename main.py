def run():
    import pygame
    import pyvidplayer2
    import visuals
    running = True
    esc = 0
    pg = pygame.display.set_mode()
    width, height = pg.get_size()
    pygame.display.set_caption("Song Comparator")
    pygame.display.set_icon(pygame.image.load("resources/assets/icon.png"))
    clock = pygame.time.Clock()
    video = None
    font = pygame.font.SysFont("Segoe UI", 48)

    manager = visuals.ButtonManager(font, spacing=50)
    manager.add_button("Playlist", size=(300, 100), radius=20)
    manager.add_button("Track", size=(300, 100), radius=20)

    while running:
        pg.fill((0, 0, 0))

        manager.layout(width // 2, height // 2 - 100)

        clicks = manager.draw_and_handle(pg)
        for c in clicks:
            if c == "Playlist":
                print("Playlist pressed")
            elif c == "Track":
                print("Track pressed")
            else:
                print(f"{c} pressed")

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_k:
                    if video:
                        video.toggle_pause()
        if keys[pygame.K_SPACE]:
            url = "https://youtu.be/Qt5wB7KXSaM"
            video = pyvidplayer2.Video(url, youtube=True)
            video.resize((width, height))
        elif keys[pygame.K_l]:
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
