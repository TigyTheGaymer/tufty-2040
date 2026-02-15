from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB332
import jpegdec
from os import listdir
import time
from pimoroni import Button
import shared

display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB332)
display.set_backlight(1.0)
j = jpegdec.JPEG(display)
gifs_dir = "/gifs"
time_delay = 0.1
last_run_time = time.ticks_ms()
current_image_index = 0
WIDTH, HEIGHT = display.get_bounds()

button_up = Button(22, invert=False)
button_down = Button(6, invert=False)
button_a = Button(7, invert=False)
button_c = Button(9, invert=False)

selected_item = 2
scroll_position = 2
target_scroll_position = 2

selected_pen = display.create_pen(255, 255, 255)
unselected_pen = display.create_pen(80, 80, 100)
background_pen = display.create_pen(50, 50, 70)
shadow_pen = display.create_pen(0, 0, 0)

BACKGROUND_PEN = display.create_pen(82, 119, 70)

# Precompute a palette for rainbow background
PALETTE_SIZE = 50
rainbow_palette = []
for i in range(PALETTE_SIZE):
    r, g, b = shared.hsv_to_rgb(i / PALETTE_SIZE, 0.5, 1)
    rainbow_palette.append(display.create_pen(r, g, b))


def draw_background():
    display.set_pen(BACKGROUND_PEN)
    display.rectangle(0, 0, WIDTH, HEIGHT)


def get_gif_folders() -> list[dict[str, str]]:
    folders = []
    for folder in listdir(gifs_dir):
        folders.append(
            {
                "dir": f"{gifs_dir}/{folder}",
                "title": folder
            }
        )
    return sorted(folders, key=lambda x: x["title"])


gif_folders = get_gif_folders()
selected_gif_dir = ""
selected_gif_images = []

# Keep track of the last opened GIF file
last_opened_file = ""

# === FPS tracking variables ===
frame_count = 0
fps_time_start = time.ticks_ms()

while True:
    t = time.ticks_ms() / 1000.0  # current time in seconds

    # === GIF playback ===
    if selected_gif_dir != "":
        if time.ticks_diff(time.ticks_ms(), last_run_time) > time_delay * 1000:
            last_run_time = time.ticks_ms()
            draw_background()

            current_file = selected_gif_images[current_image_index]["file"]

            # Only open file if it’s a new frame
            if last_opened_file != current_file:
                j.open_file(current_file)
                last_opened_file = current_file

            # Determine image position
            if selected_gif_dir in ["/gifs/andy", "/gifs/tigy_andy_kissing"]:
                image_pos_x = 0
                image_pos_y = 0
            else:
                image_pos_x = (WIDTH - HEIGHT) // 2
                image_pos_y = 0

            # Decode frame
            j.decode(image_pos_x, image_pos_y, dither=False)
            display.update()

            # Advance frame
            current_image_index += 1
            if current_image_index == len(selected_gif_images):
                current_image_index = 0

        if button_c.read():
            # Wait for the button to be released.
            while button_c.is_pressed:
                time.sleep(0.01)
            selected_gif_dir = ""
            selected_gif_images = []

    # === Menu / folder selection ===
    if selected_gif_dir == "":

        if button_up.read():
            target_scroll_position -= 1
            target_scroll_position = target_scroll_position if target_scroll_position >= 0 else len(gif_folders) - 1

        if button_down.read():
            target_scroll_position += 1
            target_scroll_position = target_scroll_position if target_scroll_position < len(gif_folders) else 0

        if button_a.read():
            # Wait for the button to be released.
            while button_a.is_pressed:
                time.sleep(0.01)
            selected_gif_dir = gif_folders[selected_item]["dir"]
            selected_gif_images = shared.get_images(selected_gif_dir)

        display.set_pen(background_pen)

        # smooth scroll
        scroll_position += (target_scroll_position - scroll_position) / 5

        grid_size = 40
        for y in range(0, 240 // grid_size):
            for x in range(0, 320 // grid_size):
                h = x + y + int(t * 5)
                h = int(h % PALETTE_SIZE)
                display.set_pen(rainbow_palette[h])
                display.rectangle(x * grid_size, y * grid_size, grid_size, grid_size)

        # determine selected item
        selected_item = round(target_scroll_position)

        for list_index, application in enumerate(gif_folders):
            distance = list_index - scroll_position
            text_size = 4 if selected_item == list_index else 3
            title_width = display.measure_text(application["title"], text_size)
            text_x = int(160 - title_width / 2)
            row_height = text_size * 5 + 20
            text_y = int(120 + distance * row_height - (row_height / 2))

            if selected_item == list_index:
                display.set_pen(shadow_pen)
                display.text(application["title"], text_x + 1, text_y + 1, -1, text_size)

            display.set_pen(selected_pen if selected_item == list_index else unselected_pen)
            display.text(application["title"], text_x, text_y, -1, text_size)

        display.update()

    # # === FPS calculation ===
    # frame_count += 1
    # if time.ticks_diff(time.ticks_ms(), fps_time_start) >= 1000:
    #     fps = frame_count
    #     print("FPS:", fps)
    #     frame_count = 0
    #     fps_time_start = time.ticks_ms()
