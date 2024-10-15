from pathlib import Path
from typing import Callable
import numpy as np
from PIL import Image
import time


def divide_image(from_: Path, to: Callable[[int], Path], div_num: int = 5):
    img = Image.open(from_).convert("RGBA")

    img_array = np.array(img)

    height, width, _ = img_array.shape

    random_mask = np.random.choice(range(div_num), size=(height, width))
    # random_mask = np.random.choice(range(div_num), size=(height))

    for i in range(div_num):
        out_img_array = np.zeros_like(img_array)
        out_img_array[random_mask == i] = img_array[random_mask == i]
        out_img = Image.fromarray(out_img_array)
        out_img.save(to(i))


if __name__ == "__main__":
    start_time = time.perf_counter()
    divide_image(Path(""), lambda i: Path(""))
    end_time = time.perf_counter()
    print(f"time: {end_time - start_time:.2f}s")
