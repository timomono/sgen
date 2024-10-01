import numpy as np
from PIL import Image
import time

start_time = time.perf_counter()

d_num = 5

image_path = "cas.png"
img = Image.open(image_path).convert("RGBA")

img_array = np.array(img)

height, width, channels = img_array.shape

# random_mask = np.random.choice(range(d_num), size=(height, width))
random_mask = np.random.choice(range(d_num), size=(height))

for i in range(d_num):
    out_img_array = np.zeros_like(img_array)
    out_img_array[random_mask == i] = img_array[random_mask == i]
    out_img = Image.fromarray(out_img_array)
    out_img.save(f"random_image{i}.png")


end_time = time.perf_counter()
print(f"time: {end_time - start_time:.2f}s")
