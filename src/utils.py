from PIL import Image, ImageChops, ImageFilter, ImageDraw, ImageFont
from math import tan, pi


def break_token_into_lines(token, chars_per_line):
    space_chars = set(' \n\t')

    new_token = ''
    hold = False
    for i, c in enumerate(token):
        if (i+1) % chars_per_line == 0 or hold:
            if c == ' ' or c == '\n':
                new_token += '\n'
                hold = False
            else:
                new_token += c
                hold = True
        else:
            new_token += c

    return new_token


# adapted from https://code-maven.com/create-images-with-python-pil-pillow
def create_base_img(word, font_fp, dim=(1000, 1000), pos=(15,15), font_size=25, fill=0, bg=255):
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


def underline(img, font_size, border):
    w, h = img.size
    underlined = img.copy()
    draw = ImageDraw.Draw(underlined)
    h_line = font_size + 3
    n_lines = int((h - 2*border) / h_line) + 1
    for i in range(n_lines):
        draw.line((border, h-border-i*h_line, w-border, h-border-i*h_line), fill=0, width=2)
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


