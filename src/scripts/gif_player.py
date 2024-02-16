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
time_delay = 0.2
last_run_time = time.time()
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


def draw_background():
    display.set_pen(BACKGROUND_PEN)
    display.rectangle(0, 0, WIDTH, HEIGHT)


def get_gif_folders() -> list[dict[str, str]]:
    folders = []
    for folder in listdir(gifs_dir):
        folders.append(
            {
                "dir": gifs_dir + "/" + folder,
                "title": folder
            }
        )

    # sort the application list alphabetically by title and return the list
    return sorted(folders, key=lambda x: x["title"])


gif_folders = get_gif_folders()
selected_gif_dir = ""
selected_gif_images = []

while True:
    t = time.ticks_ms() / 1000.0

    if selected_gif_dir != "":
        if last_run_time <= time.time() - time_delay:
            draw_background()
            last_run_time = time.time()
            j.open_file(selected_gif_images[current_image_index]["file"])

            # full width but not full height
            if selected_gif_dir == "/gifs/3":
                image_pos_x = 0
                image_pos_y = 0  # TODO center in y

            # full height but not full width
            else:
                image_pos_x = (WIDTH - HEIGHT) // 2  # center image
                image_pos_y = 0

            j.decode(image_pos_x, 0, dither=False)
            display.update()
            current_image_index += 1
            if current_image_index == len(selected_gif_images):
                current_image_index = 0

        if button_c.read():
            # Wait for the button to be released.
            while button_a.is_pressed:
                time.sleep(0.01)
            selected_gif_dir = ""
            selected_gif_images = []

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
        display.clear()

        scroll_position += (target_scroll_position - scroll_position) / 5

        grid_size = 40
        for y in range(0, 240 // grid_size):
            for x in range(0, 320 // grid_size):
                h = x + y + int(t * 5)
                h = h / 50.0
                r, g, b = shared.hsv_to_rgb(h, 0.5, 1)

                display.set_pen(display.create_pen(r, g, b))
                display.rectangle(x * grid_size, y * grid_size, grid_size, grid_size)

        # work out which item is selected (closest to the current scroll position)
        selected_item = round(target_scroll_position)

        for list_index, application in enumerate(gif_folders):
            distance = list_index - scroll_position

            text_size = 4 if selected_item == list_index else 3

            # center text horixontally
            title_width = display.measure_text(application["title"], text_size)
            text_x = int(160 - title_width / 2)

            row_height = text_size * 5 + 20

            # center list items vertically
            text_y = int(120 + distance * row_height - (row_height / 2))

            # draw the text, selected item brightest and with shadow
            if selected_item == list_index:
                display.set_pen(shadow_pen)
                display.text(application["title"], text_x + 1, text_y + 1, -1, text_size)

            text_pen = selected_pen if selected_item == list_index else unselected_pen
            display.set_pen(text_pen)
            display.text(application["title"], text_x, text_y, -1, text_size)

        display.update()
