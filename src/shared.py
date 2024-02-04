from os import listdir


def hsv_to_rgb(h: float, s: float, v: float) -> tuple[float, float, float]:
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    v = int(v * 255)
    t = int(t * 255)
    p = int(p * 255)
    q = int(q * 255)
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


def get_images(images_dir) -> list[dict[str, str]]:
    # fetch a list of the applications that are stored in the filesystem
    images = []
    for file in listdir(images_dir):
        if file.endswith(".jpg"):
            # remove last 4 characters from filename (.jpg)
            title = file[:-4]
            images.append(
                {
                    "file": images_dir + "/" + file,
                    "title": title
                }
            )
    return sorted(images, key=lambda x: x["title"])