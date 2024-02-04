from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from jpegdec import JPEG
import time
from pimoroni import Button
import shared

display = PicoGraphics(display=DISPLAY_TUFTY_2040)
j = JPEG(display)
image_dir = "/images"
time_delay = 2
button_c = Button(9, invert=False)
last_run_time = time.time()
current_image_index = 0


images = shared.get_images(image_dir)

while True:

    if last_run_time <= time.time() - time_delay:
        last_run_time = time.time()
        j.open_file(images[current_image_index]["file"])
        j.decode()
        display.update()
        current_image_index += 1
        if current_image_index == len(images):
            current_image_index = 0
