from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageFont
from math import tan, pi


# adapted from https://code-maven.com/create-images-with-python-pil-pillow
def create_base_img(word, font_fp, dim=(1000, 100), pos=(25,25), font_size=50, fill=0, bg=255):
    img = Image.new('1', dim, color=bg)
    font = ImageFont.truetype(font_fp, font_size)
    draw = ImageDraw.Draw(img)
    draw.text(pos, word, font=font, fill=fill)
    return img

# crop image to remove empty space around text
# adapted from https://gist.github.com/mattjmorrison/932345
def trim(img, border):
    w, h = img.size
    bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox(); l, t, r, b = bbox
    
    if border:
        l = max(0, l-border)
        t = max(0, t-border)
        r = min(w-1, r+border)
        b = min(h-1, b+border)
        bbox = (l, t, r, b)

    if bbox:
        return img.crop(bbox)


# adapted from https://github.com/zevisert/Imagyn/blob/master/imagyn/synthesis/transform.py
def skew(img, angle):
    w, h = img.size
    angle_rad = angle * (pi / 180)
    xshift = tan(abs(angle_rad)) * h
    new_w = w + int(xshift)

    if new_w < 0:
        return img

    img = img.transform(
        (new_w, h),
        Image.AFFINE,
        (1, angle_rad, -xshift if angle_rad > 0 else 0, 0, 1, 0),
        Image.BICUBIC,
        fillcolor=img.getpixel((0,0))
    )
    return img


def rotate(img, angle):
    return img.rotate(angle, expand=True, resample=Image.BICUBIC, fillcolor=img.getpixel((0,0)))


def blur(img, radius):
    return img.filter(ImageFilter.GaussianBlur(radius=radius))


def underline(img, border, font_size):
    w, h = img.size
    x, y = (border, border)
    v_offset = int(0.15 * font_size)
    underlined = img.copy()
    draw = ImageDraw.Draw(underlined)
    draw.line((x, y + h - v_offset, x + w - border, y + h - v_offset), fill=0, width=4)
    return underlined


def make_modified_fp(mod, fp):
    fp_split = fp.split('.')
    new_fp_split = fp_split[:-1] + [mod] + fp_split[-1:]
    mod_fp = '.'.join(new_fp_split)
    return mod_fp


def apply_modification_and_save(img, img_fp, mod_name, mod_func, ret=False):
    img = mod_func(img)
    img_fp = make_modified_fp(mod_name, img_fp)
    img.save(img_fp)

    if ret:
        return img


