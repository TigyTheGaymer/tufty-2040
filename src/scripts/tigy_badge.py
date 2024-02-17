# A retro badge with photo and QR code.
# Copy your image to your Tufty alongside this example - it should be a 120 x 120 jpg.

from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB332
from pimoroni import Button
import time
import jpegdec
import qrcode
import shared

display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB332)
button_a = Button(7, invert=False)
button_b = Button(8, invert=False)
button_c = Button(9, invert=False)

WIDTH, HEIGHT = display.get_bounds()

LIGHTEST = display.create_pen(208, 208, 88)
DARK = display.create_pen(82, 119, 70)
DARKEST = display.create_pen(64, 80, 16)

# Change your badge and QR details here!
NAME = "Tigy"
QR_TEXT = "https://twitter.com/TigyTheGaymer"
IMAGES_DIR = "/badge_images"
TIME_DELAY = 10

# Some constants we'll use for drawing
BORDER_SIZE = 4
PADDING = 10
NAME_TEXT_SIZE = 6


class ColorCycle:
    def __init__(self, steps_per_color):
        self.steps_per_color = steps_per_color
        self.color_generator = self.smooth_color_cycle()

    def smooth_color_cycle(self):
        colors = [
            (255, 0, 0),  # Red
            (255, 128, 0),  # Orange
            (255, 255, 0),  # Yellow
            (128, 255, 0),  # Lime
            (0, 255, 0),  # Green
            (0, 255, 128),  # Aqua
            (0, 255, 255),  # Cyan
            (0, 128, 255),  # Sky Blue
            (0, 0, 255),  # Blue
            (127, 0, 255),  # Indigo
            (255, 0, 255)  # Magenta
        ]

        while True:
            for i in range(len(colors) - 1):
                for step in range(self.steps_per_color):
                    # Interpolate between the two colors
                    color = tuple(
                        int(colors[i][j] + (colors[i + 1][j] - colors[i][j]) * step / self.steps_per_color) for j in
                        range(3))
                    yield color

    def next_color(self):
        return display.create_pen(*next(self.color_generator))


color_cycle = ColorCycle(30)


def draw_badge():
    # draw background
    display.set_pen(DARK)
    display.rectangle(BORDER_SIZE, BORDER_SIZE, WIDTH - (BORDER_SIZE * 2), HEIGHT - (BORDER_SIZE * 2))

    # draw name text
    display.set_pen(LIGHTEST)
    display.set_font("bitmap8")
    title_width = display.measure_text(NAME, NAME_TEXT_SIZE)
    text_draw_pos_x = int(160 - title_width / 2)  # center
    text_draw_pos_y = BORDER_SIZE + PADDING
    display.text(NAME, text_draw_pos_x, text_draw_pos_y, WIDTH, NAME_TEXT_SIZE)


def draw_badge_border():
    # draw border
    display.set_pen(color_cycle.next_color())
    display.line(0, 0, WIDTH, 0, 10)
    display.line(WIDTH, 0, WIDTH, HEIGHT, 10)
    display.line(WIDTH, HEIGHT, 0, HEIGHT, 10)
    display.line(0, HEIGHT, 0, 0, 10)


def show_photo(image):
    j = jpegdec.JPEG(display)

    # Open the JPEG file
    j.open_file(image)

    # Decode the JPEG
    text_height = NAME_TEXT_SIZE * 5 + 15
    image_draw_pos_x = BORDER_SIZE
    image_draw_pos_y = BORDER_SIZE + PADDING + text_height + PADDING
    j.decode(image_draw_pos_x, image_draw_pos_y, dither=False)


def measure_qr_code(size, code):
    w, h = code.get_size()
    module_size = int(size / w)
    return module_size * w, module_size


def draw_qr_code(ox, oy, size, code):
    size, module_size = measure_qr_code(size, code)
    display.set_pen(LIGHTEST)
    display.rectangle(ox, oy, size, size)
    display.set_pen(DARKEST)
    for x in range(size):
        for y in range(size):
            if code.get_module(x, y):
                display.rectangle(ox + x * module_size, oy + y * module_size, module_size, module_size)


def show_qr():
    display.set_pen(DARK)
    display.clear()

    code = qrcode.QRCode()
    code.set_text(QR_TEXT)

    size, module_size = measure_qr_code(HEIGHT, code)
    left = int((WIDTH // 2) - (size // 2))
    top = int((HEIGHT // 2) - (size // 2))
    draw_qr_code(left, top, HEIGHT, code)


badge_mode = "photo"
last_run_time = time.time()
last_run_time_border = time.time()
current_image_index = 0
images = shared.get_images(IMAGES_DIR)

# draw the badge for the first time
draw_badge()
draw_badge_border()
show_photo(images[current_image_index]["file"])
current_image_index += 1
display.update()

while True:

    if button_b.is_pressed:
        if badge_mode == "photo":
            badge_mode = "qr"
            show_qr()
        else:
            badge_mode = "photo"
            draw_badge()

    if badge_mode == "photo":
        if last_run_time <= time.time() - TIME_DELAY:
            last_run_time = time.time()
            show_photo(images[current_image_index]["file"])
            current_image_index += 1
            if current_image_index == len(images):
                current_image_index = 0
        if last_run_time_border <= time.time() - 0.2:
            last_run_time_border = time.time()
            draw_badge_border()

    display.update()
