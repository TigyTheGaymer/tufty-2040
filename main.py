from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from jpegdec import JPEG
from os import listdir
from time import sleep

display = PicoGraphics(display=DISPLAY_TUFTY_2040)
j = JPEG(display)
image_dir = "/images"

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

def infinite_loop(my_list):
    while True:
        for element in my_list:
            yield element
        

for image in infinite_loop(get_images()):

    j.open_file(image["file"])
    j.decode()
    display.update()
    sleep(2)

    
