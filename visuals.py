import pygame

import data


class Button:
    """Represents a single rounded button with pixel-perfect rounded-corner hit-testing,
    hover and click visuals, and an enabled/disabled state."""

    def __init__(self, text, id, font, size=None, radius=20,
                 base_color=(255, 255, 255), hover_color=(200, 200, 200),
                 click_color=(150, 150, 150), disabled_color=(100, 100, 100),
                 padding_y=16, details=None):
        """Create a Button.

        Parameters
        ----------
            text (str): label shown on the button
            font (pygame.font.Font): font used to render the label
            size (tuple): (width, height) where height can be None to auto-calculate
            radius (int): rounded corner radius
            base_color/hover_color/click_color/disabled_color (tuples): RGB colors
            padding_y (int): vertical padding used when auto-calculating height
        """
        self.text = text
        self.id = id
        self.details = details
        self.font = font
        self.padding_y = padding_y
        # calculate the width and height if not given
        if size is None:
            txt_surf = self.font.render(self.text, True, (0, 0, 0))
            txt_w, txt_h = txt_surf.get_size()
            self.w = max(100, txt_w + self.padding_y * 2)
            self.h = max(100, txt_h + self.padding_y * 2)
        # use given size
        else:
            self.w = int(size[0])
            # allow height to be None -> auto-calculate using font line size + padding
            self.h = int(size[1]) if len(size) > 1 and size[1] is not None else None
        self.radius = radius
        self.base_color = base_color
        self.hover_color = hover_color
        self.click_color = click_color
        self.disabled_color = disabled_color

        # auto-calculate height from font if needed
        if self.h is None:
            txt_h = self.font.get_linesize()  # line height
            self.h = txt_h + self.padding_y * 2

        # rect stores position and size in content coordinates (managed by ButtonManager)
        self.rect = pygame.Rect(0, 0, self.w, self.h)
        self.x = 0
        self.y = 0

        self.enabled = True

        # surfaces and mask prepared for fast rendering and pixel-precise hit detection
        self._create_surfaces()

        # runtime state flags
        self.hover = False
        self.pressed = False

    def _create_surfaces(self):
        """Builds the button surfaces (base / hover / click / disabled) and the mask.
        Surfaces are RGBA with rounded rects drawn; mask is used for pixel-perfect hit tests."""
        txt = self.font.render(self.text, True, (0, 0, 0))

        def make_surf(color):
            """Helper: create a single surface for the given solid color and render text centered."""
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            pygame.draw.rect(s, color + (255,), s.get_rect(), border_radius=self.radius)
            s.blit(txt, (self.w // 2 - txt.get_width() // 2, self.h // 2 - txt.get_height() // 2))
            return s

        # create all surfaces and a mask
        self.surf_base = make_surf(self.base_color)
        self.surf_hover = make_surf(self.hover_color)
        self.surf_click = make_surf(self.click_color)
        self.surf_disabled = make_surf(self.disabled_color)
        self.mask = pygame.mask.from_surface(self.surf_base)

    def get_id(self, button):
        return button.id

    def set_pos(self, x, y):
        """Set the top-left position of this button in content coordinates.

        Parameters
        ----------
            x (int): X position
            y (int): Y position
        """
        self.x = int(x)
        self.y = int(y)
        self.rect.topleft = (int(x), int(y))

    def set_enabled(self, state: bool = True):
        """Enable or disable the button.

        Parameters
        ----------
            state (bool): True to enable; False to disable (default: True)
        """
        self.enabled = bool(state)

    def draw_and_update(self, surface, mouse_pos, mouse_down):
        """Draw the button at its rect and update hover/click visual state.
        This method expects 'self.rect' to be already positioned in screen coordinates.
        For content + viewport usage, ButtonManager draws buttons manually (so this method
        is useful when buttons can't be scrolled).

        Parameters
        ----------
            surface (pygame.Surface): target surface to draw onto
            mouse_pos (tuple): current mouse position in screen coordinates
            mouse_down (bool): whether left mouse is currently down

        Returns
        -------
            bool: True if the button is being pressed (mouse-down on an opaque pixel)
        """
        if not self.enabled:
            surface.blit(self.surf_disabled, self.rect.topleft)
            return False

        # local mouse coords relative to button top-left
        lx = int(mouse_pos[0] - self.rect.x)
        ly = int(mouse_pos[1] - self.rect.y)
        inside = False

        # bounds check first, then mask lookup
        if 0 <= lx < self.w and 0 <= ly < self.h:
            if self.mask.get_at((lx, ly)):
                inside = True
        self.hover = inside

        # choose visual based on hover / pressing or neither
        if inside and mouse_down:
            surface.blit(self.surf_click, self.rect.topleft)
            return True
        elif inside:
            surface.blit(self.surf_hover, self.rect.topleft)
        else:
            surface.blit(self.surf_base, self.rect.topleft)
        return False

    def set_alpha(self, alpha):
        self.surf_base.set_alpha(alpha)
        self.surf_hover.set_alpha(alpha)
        self.surf_click.set_alpha(alpha)
        self.surf_disabled.set_alpha(alpha)

    def reset_alpha(self):
        self.surf_base.set_alpha(255)
        self.surf_hover.set_alpha(255)
        self.surf_click.set_alpha(255)
        self.surf_disabled.set_alpha(255)


class ButtonManager:
    """Manages multiple Buttons, automatic wrapping layout, vertical scrolling,
    and click detection with pixel-perfect masks."""

    def __init__(self, font, spacing=50, vspacing=20, scroll_speed=40):
        """Create a ButtonManager.

        Parameters
        ----------
            font (pygame.font.Font): font passed to new Buttons
            spacing (int): horizontal spacing between buttons
            vspacing (int): vertical spacing between rows
            scroll_speed (int): pixels to scroll per mousewheel tick
        """
        self.font = font
        self.spacing = spacing
        self.vspacing = vspacing
        self.buttons = []
        self._prev_mouse_down = False

        # scrolling state
        self.viewport = pygame.Rect(0, 0, 800, 600)  # default; set from set_viewport()
        self.scroll_y = 0
        self.scroll_speed = scroll_speed
        self._content_height = 0
        self._max_scroll = 0
        self.x = 0
        self.y = 0

    def add_button(self, text, id, **kwargs):
        """Create and add a new Button to the manager.

        Returns
        -------
            Button: the created button instance
        """
        b = Button(text, id, self.font, **kwargs)
        self.buttons.append(b)
        return b

    def clear(self):
        """Remove all buttons and reset scroll/layout state."""
        self.buttons.clear()
        self.scroll_y = 0
        self._content_height = 0
        self._max_scroll = 0

    def set_enabled(self, text, state: bool = True):
        """Enable/disable a button by its exact text label.

        Returns
        -------
            bool: True if a button was found and updated, False otherwise
        """
        for b in self.buttons:
            if b.text == text:
                b.set_enabled(state)
                return True
        return False

    def disable_all(self):
        """Disable every button managed by this ButtonManager."""
        for button in self.buttons:
            button.set_enabled(False)

    def enable_all(self):
        """Enable every button managed by this ButtonManager."""
        for button in self.buttons:
            button.set_enabled(True)

    def handle_event(self, event):
        """Call from the event loop. Handles mouse wheel scrolling."""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * self.scroll_speed
            self.scroll_y = max(0, min(self.scroll_y, self._max_scroll))

    def set_viewport(self, rect: pygame.Rect):
        """Set the visible area (viewport) where buttons are drawn and scrolled.

        Parameters
        ----------
            rect (pygame.Rect): viewport rectangle in screen coordinates
        """
        self.x = rect.x
        self.y = rect.y
        self.viewport = rect.copy()
        self.scroll_y = max(0, min(self.scroll_y, getattr(self, "_max_scroll", 0)))

    def layout(self, center_x, center_y, max_width):
        """Layout buttons into rows in content space.

        The function wraps buttons when row width would exceed max_width. If the resulting
        content height fits inside the viewport, the whole block is vertically centered.
        If content is taller than the viewport, it is top-aligned and scrolling is enabled.

        Parameters
        ----------
            center_x (int): center x of viewport (not used for vertical placement)
            center_y (int): center y of viewport (not used when scrolling)
            max_width (int): available horizontal width for content (usually viewport.w)
        """
        if not self.buttons:
            self._content_height = 0
            self._max_scroll = 0
            return

        # build rows with wrapping
        rows = []
        current_row = []
        row_width = 0

        for b in self.buttons:
            bw = b.w
            next_width = bw if not current_row else row_width + self.spacing + bw
            if current_row and next_width > max_width:
                rows.append(current_row)
                current_row = [b]
                row_width = bw
            else:
                current_row.append(b)
                row_width = next_width if len(current_row) > 1 else bw
        if current_row:
            rows.append(current_row)

        # calculate total height of content
        total_h = sum(max(btn.h for btn in row) for row in rows) + self.vspacing * (len(rows) - 1)
        self._content_height = total_h

        # calculate max scroll value (content taller than viewport)
        self._max_scroll = max(0, total_h - self.viewport.h)

        # decide start_y in content-space:
        if total_h <= self.viewport.h:
            # content fits -> center vertically inside viewport; forbid scrolling
            start_y = (self.viewport.h - total_h) // 2
            self.scroll_y = 0
        else:
            # content taller -> align to top; allow scrolling
            start_y = 0
            self.scroll_y = max(0, min(self.scroll_y, self._max_scroll))

        # place buttons relative to content origin (0,0)
        y = start_y
        for row in rows:
            row_h = max(btn.h for btn in row)
            row_w = sum(btn.w for btn in row) + self.spacing * (len(row) - 1)
            start_x = int((max_width - row_w) // 2)
            x = start_x
            for btn in row:
                btn.set_pos(x, y)
                x += btn.w + self.spacing
            y += row_h + self.vspacing

    def draw_and_handle(self, surface, mouse_up):
        """Draw buttons inside the configured viewport and return clicked button texts.

        This function:
          - clips rendering to the viewport
          - translates content positions to screen positions applying scroll
          - performs pixel-perfect mask checks against visible button pixels
          - returns a list of button.text strings that were clicked

        Parameters
        ----------
            surface (pygame.Surface): the main screen surface

        Returns
        -------
            list[str]: text of buttons clicked this frame
        """
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]

        # restrict drawing to viewport
        old_clip = surface.get_clip()
        surface.set_clip(self.viewport)

        vx, vy = self.viewport.topleft

        clicked_id = None
        clicked_text = None
        clicked_details = None

        for b in self.buttons:
            # calculate screen draw position = viewport.topleft + content_pos - scroll_y
            draw_x = vx + int(b.rect.x)
            draw_y = vy + int(b.rect.y) - int(self.scroll_y)

            # skip drawing fully outside viewport
            if draw_y + b.h < vy or draw_y > vy + self.viewport.h:
                continue

            # local mouse relative to drawn button position
            local_mouse_x = mouse_pos[0] - draw_x
            local_mouse_y = mouse_pos[1] - draw_y

            # if disabled -> blit disabled surface
            if not b.enabled:
                surface.blit(b.surf_disabled, (draw_x, draw_y))
                continue

            # safe mask check with local coords
            lx = int(local_mouse_x)
            ly = int(local_mouse_y)
            inside = False
            if 0 <= lx < b.w and 0 <= ly < b.h:
                try:
                    if b.mask.get_at((lx, ly)):
                        inside = True
                except IndexError:
                    inside = False

            # draw the correct visual for this state
            if inside and mouse_up:
                is_clicked = True
            elif inside and mouse_down:
                surface.blit(b.surf_click, (draw_x, draw_y))
                is_clicked = False
            elif inside and not mouse_down:
                surface.blit(b.surf_hover, (draw_x, draw_y))
                is_clicked = False
            else:
                surface.blit(b.surf_base, (draw_x, draw_y))
                is_clicked = False

            # click edge detection must only trigger when the click occurs inside visible button
            if is_clicked and not self._prev_mouse_down:
                clicked_id = b.id
                clicked_text = b.text
                clicked_details = b.details

        # restore clip and update the previous mouse state
        surface.set_clip(old_clip)
        self._prev_mouse_down = mouse_up
        return clicked_id, clicked_text, clicked_details

    def is_mouse_over_any_button(self, mouse_pos):
        """Checks if the mouse is currently over any button (active or disabled doesn't matter).

        Parameters
        ----------
            mouse_pos (tuple): mouse position in screen coordinates

        Returns
        -------
            bool: True if mouse is over any button, otherwise False
        """
        vx, vy = self.viewport.topleft

        for b in self.buttons:
            # calculate screen position of this button
            draw_x = vx + int(b.rect.x)
            draw_y = vy + int(b.rect.y) - int(self.scroll_y)

            # skip buttons completely outside viewport
            if draw_y + b.h < vy or draw_y > vy + self.viewport.h:
                continue

            # local mouse coordinates relative to button position
            local_mouse_x = mouse_pos[0] - draw_x
            local_mouse_y = mouse_pos[1] - draw_y

            # check if mouse is within button bounds and on visible pixel
            if 0 <= local_mouse_x < b.w and 0 <= local_mouse_y < b.h:
                try:
                    if b.mask.get_at((int(local_mouse_x), int(local_mouse_y))):
                        return True
                except IndexError:
                    continue
        return False


def calc_cover(cover: str, width, height, coverFound=True):
    """Load and scale a track cover image to fill the screen while preserving the aspect ratio.

    Parameters
    ----------
        cover (str): track "cover" filename
        width (int): available width (usually screen width)
        height (int): available height (usually screen height)

    Returns
    -------
        tuple: (scaledCoverSurface, coverRect) where coverRect is centered on screen
    """
    coverImage = pygame.image.load((data.coverfolder + cover if coverFound else "resources/assets/tnf.png"))
    coverWidth, coverHeight = coverImage.get_size()
    aspectRatio = coverWidth / coverHeight

    # choose the scale type depending on image orientation
    if coverWidth > coverHeight:
        coverWidth = width
        coverHeight = int(coverWidth / aspectRatio)
    else:
        coverHeight = height
        coverWidth = int(coverHeight * aspectRatio)
    if coverFound:
        scaledCover = pygame.transform.smoothscale(coverImage, (coverWidth, coverHeight))
    else:
        scaledCover = coverImage
    coverRect = scaledCover.get_rect()
    coverRect.center = (width // 2, height // 2)
    return scaledCover, coverRect


star = pygame.image.load("resources/assets/star.png")
star_highlighted = pygame.image.load("resources/assets/star_highlighted.png")
star_filled = pygame.image.load("resources/assets/star_filled.png")


class StarRating:
    """Manages the state, event handling, and drawing for the rating screen."""

    def __init__(self, x, y, label, font):
        self.x = x
        self.y = y
        self.label = label
        self.font = font
        # state: rating is the clicked value, hover_rating is for visual feedback
        self.rating = 0
        self.hover_rating = 0
        # create rectangles for collision detection
        star_width = star.get_width()
        self.star_rects = [star.get_rect(topleft=(self.x + star_width * i, self.y)) for i in range(5)]

    def handle_event(self, event):
        """Processes mouse events to update the widget state."""
        mouse_pos = pygame.mouse.get_pos()
        # update hover state based on current mouse position
        self.hover_rating = 0
        for i in range(4, -1, -1):
            if self.star_rects[i].collidepoint(mouse_pos):
                self.hover_rating = i + 1
                break
        # process clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover_rating > 0:  # if the click was on a star
                self.rating = self.hover_rating
        return self.star_rects[-1]

    def draw(self, surface):
        """Draws the label and stars based on the current state."""
        # draw the label text
        text_surface = self.font.render(self.label, True, (255, 255, 255))
        surface.blit(text_surface, (self.x - 350, self.y + (star.get_height() - text_surface.get_height()) // 2))
        # draw the 5 stars
        for i in range(5):
            star_index = i + 1
            star_to_draw = star  # Default texture: star
            # clicked state takes visual priority over the hover state
            if star_index <= self.rating:
                star_to_draw = star_filled
            elif star_index <= self.hover_rating:
                star_to_draw = star_highlighted
            surface.blit(star_to_draw, self.star_rects[i].topleft)
        return self.rating


def setup_voting_widgets(width, height, font, lang):
    """Creates and returns a list of all interactive StarRating widgets."""
    widgets = []
    categories = ["Relatability" if not lang else lang["voting"]["relatability"],
                  "Lyrics Quality" if not lang else lang["voting"]["lyrics_quality"],
                  "Beat Quality" if not lang else lang["voting"]["beat_quality"],
                  "Beat Taste" if not lang else lang["voting"]["beat_taste"]]
    y_levels = len(categories) * 2 + 1
    start_x = width // 5
    text_rect = font.render(categories[0], True, (255, 255, 255)).get_rect()

    for i, category in enumerate(categories):
        widget_y = (height // y_levels) * (i * 2) + (height // y_levels - text_rect.height // 2)
        widgets.append(StarRating(start_x, widget_y, category, font))
    return widgets


def show_voting_screen(surface, widgets):
    """Draws the voting widgets."""
    ratings = []
    for widget in widgets:
        rating = widget.draw(surface)
        ratings.append(rating)
    return ratings
