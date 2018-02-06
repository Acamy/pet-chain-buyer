from PIL import Image
import pytesseract
from PIL import ImageFile
from matplotlib import animation
import matplotlib.pyplot as plt

ImageFile.LOAD_TRUNCATED_IMAGES = True

# 二值化算法
def binarizing(img,threshold):
    pixdata = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if pixdata[x, y] < threshold:
                pixdata[x, y] = 0
            else:
                pixdata[x, y] = 255
    return img


# 去除干扰线算法
def depoint(img):   #input: gray image
    pixdata = img.load()
    w,h = img.size
    for y in range(1,h-1):
        for x in range(1,w-1):
            count = 0
            if pixdata[x,y-1] > 245:
                count = count + 1
            if pixdata[x,y+1] > 245:
                count = count + 1
            if pixdata[x-1,y] > 245:
                count = count + 1
            if pixdata[x+1,y] > 245:
                count = count + 1
            if count > 2:
                pixdata[x,y] = 255
    return img

def ocr_img(image):
    # win环境
    # tesseract 路径
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files (x86)\\Tesseract-OCR\\tesseract'
    # 语言包目录和参数
    tessdata_dir_config = '--tessdata-dir "C:\\Program Files (x86)\\Tesseract-OCR\\tessdata" --psm 6'


    # 转化为灰度图
    image = image.convert('L')
    # 把图片变成二值图像
    image = binarizing(image, 190)

    img=depoint(image)
    #img.show()

    result = pytesseract.image_to_string(image, config=tessdata_dir_config)
    return result

fig = plt.figure()
img = Image.open('captcha.jpg')
im = plt.imshow(img, animated=True)

def updatefig(s):
    im.set_array(Image.open('captcha.jpg'))
    return im
if __name__ == '__main__':
    # img = Image.open("./captcha.jpg")
    # print(ocr_img(img))

    ani = animation.FuncAnimation(fig, updatefig, interval=5, blit=True)
    plt.show()