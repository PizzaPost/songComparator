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
    def play_track(url=None, filename=None):
        global video
        if url:
            video=pyvidplayer2.Video(url, youtube=True)
            video.preview()
        elif filename:
            video=pyvidplayer2.Video(filename)
            video.preview()
    while running:
        pg.fill((0,0,0))
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        keys=pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            play_track(url="https://youtu.be/Qt5wB7KXSaM?si=Yq5hiKMj26jyFSe4")
        if keys[pygame.K_ESCAPE]:
            esc+=1
            pg.fill((255,0,0), (0, height-50, width//200*esc, 50))
        else:
            esc=0
        if esc==215:
            running=False
        pygame.display.update()
        clock.tick(120)
    pygame.quit()
if __name__ == "__main__":
    run()