import pygame

class Button:
    def __init__(self, text, font, size=(300,100), radius=20,
                 base_color=(255,255,255), hover_color=(200,200,200), click_color=(150,150,150)):
        self.text = text
        self.font = font
        self.w, self.h = size
        self.radius = radius
        self.base_color = base_color
        self.hover_color = hover_color
        self.click_color = click_color

        self.rect = pygame.Rect(0,0,self.w,self.h)
        self._create_surfaces()

        # runtime state
        self.hover = False
        self.pressed = False

    def _create_surfaces(self):
        txt = self.font.render(self.text, True, (0,0,0))
        def make_surf(color):
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            pygame.draw.rect(s, color + (255,), s.get_rect(), border_radius=self.radius)
            s.blit(txt, (self.w//2 - txt.get_width()//2, self.h//2 - txt.get_height()//2))
            return s
        self.surf_base = make_surf(self.base_color)
        self.surf_hover = make_surf(self.hover_color)
        self.surf_click = make_surf(self.click_color)
        # mask only needs to be built from an opaque-surf (base or hover) since alpha layout same
        self.mask = pygame.mask.from_surface(self.surf_base)

    def set_pos(self, x, y):
        self.rect.topleft = (x, y)

    def draw_and_update(self, surface, mouse_pos, mouse_down):
        # local coords
        lx = mouse_pos[0] - self.rect.x
        ly = mouse_pos[1] - self.rect.y
        inside = False
        if 0 <= lx < self.w and 0 <= ly < self.h:
            try:
                if self.mask.get_at((int(lx), int(ly))):
                    inside = True
            except IndexError:
                inside = False

        self.hover = inside

        if inside and mouse_down:
            self.pressed = True
            surface.blit(self.surf_click, self.rect.topleft)
            # return that it's pressed on mouse-down (edge detection handled externally)
        elif inside:
            surface.blit(self.surf_hover, self.rect.topleft)
            self.pressed = False
        else:
            surface.blit(self.surf_base, self.rect.topleft)
            self.pressed = False

        return inside and mouse_down  # True while left mouse is down over an opaque pixel

class ButtonManager:
    def __init__(self, font, spacing=50):
        self.font = font
        self.spacing = spacing
        self.buttons = []

        # for simple click-edge detection
        self._prev_mouse_down = False

    def add_button(self, text, **kwargs):
        b = Button(text, self.font, **kwargs)
        self.buttons.append(b)
        return b

    def layout(self, center_x, center_y):
        # center the block of buttons horizontally and vertically around center_x, center_y
        n = len(self.buttons)
        if n == 0:
            return
        total_w = sum(b.w for b in self.buttons) + self.spacing * (n - 1)
        start_x = int(center_x - total_w // 2)
        y = int(center_y - self.buttons[0].h // 2)
        x = start_x
        for b in self.buttons:
            b.set_pos(x, y)
            x += b.w + self.spacing

    def draw_and_handle(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        clicked_names = []

        for b in self.buttons:
            is_down = b.draw_and_update(surface, mouse_pos, mouse_down)
            # detect mouse-down edge (only fire once when button transitions from up->down)
            if is_down and not self._prev_mouse_down:
                clicked_names.append(b.text)
        self._prev_mouse_down = mouse_down
        return clicked_names

    def clear(self):
        self.buttons.clear()