# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

def updatefig(self):
    try:
        im.set_array(Image.open('captcha.jpg'))
    except Exception as e:
        pass
    return im,

fig = plt.figure()
img = Image.open('captcha.jpg')
im = plt.imshow(img, animated=True)
ani = animation.FuncAnimation(fig, updatefig, interval=1, blit=True)
plt.show()
