def run():
    import pygame
    import pyvidplayer2
    running=True
    esc=0
    pg=pygame.display.set_mode()
    width, height=pg.get_size()
    pygame.display.set_caption("Song Comparator")
    pygame.display.set_icon(pygame.image.load("resources/assets/icon.png"))
    clock=pygame.time.Clock()
    video=None
    while running:
        pg.fill((0,0,0))
        keys=pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            elif event.type==pygame.KEYUP:
                if event.key==pygame.K_k:
                    if video:
                        video.toggle_pause()
        if keys[pygame.K_SPACE]:
            url="https://youtu.be/Qt5wB7KXSaM"
            video = pyvidplayer2.Video(url, youtube=True)
            video.resize((width, height))
        elif keys[pygame.K_l]:
            if video:
                video.seek(5)
        elif keys[pygame.K_j]:
            if video:
                video.seek(-5)
        if esc==215:
            running=False
        if video:
            video.draw(pg, (0,0))
        if keys[pygame.K_ESCAPE]:
            esc+=1
            pg.fill((255,0,0), (0, height-50, width//200*esc, 50))
        else:
            esc=0
        pygame.display.update()
        clock.tick(120)
    pygame.quit()
if __name__ == "__main__":
    run()