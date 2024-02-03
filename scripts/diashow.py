from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from jpegdec import JPEG
from os import listdir
import time
from pimoroni import Button

display = PicoGraphics(display=DISPLAY_TUFTY_2040)
j = JPEG(display)
image_dir = "/images"
time_delay = 2
button_c = Button(9, invert=False)
last_run_time = time.time()
current_image_index = 0

def get_images() -> list[dict[str, str]]:
    # fetch a list of the applications that are stored in the filesystem
    images = []
    for file in listdir(image_dir):
        if file.endswith(".jpg"):
            # remove last 4 characters from filename (.jpg)
            title = file[:-4]
            images.append(
                {
                    "file": image_dir + "/" + file,
                    "title": title
                }
            )

    # sort the application list alphabetically by title and return the list
    return sorted(images, key=lambda x: x["title"])    

images = get_images()

while True:
          
    if last_run_time <= time.time() - time_delay:
        last_run_time = time.time()
        j.open_file(images[current_image_index]["file"])
        j.decode()
        display.update()
        current_image_index += 1
        if current_image_index == len(images):
            current_image_index = 0
    

    
