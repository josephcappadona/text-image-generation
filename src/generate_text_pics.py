# inspired by https://blogs.dropbox.com/tech/2017/04/creating-a-modern-ocr-pipeline-using-computer-vision-and-deep-learning/
from sys import argv
from glob import iglob
from os import makedirs
from re import sub, UNICODE
from utils import create_base_img, trim, rotate, blur, skew, underline, apply_modification_and_save
from PIL import Image, ImageDraw, ImageFont


BASE_IMG_DIM = (1000, 100)
TEXT_POS = (25,25)
FONT_SIZE = 50
BORDER = 3

ROTATE_ANGLE = 5
SKEW_ANGLE = 15
BLUR_RADIUS = 2

BLACK = 0
WHITE = 255

USAGE = "\nUSAGE:  python generate_text_pics.py CORPUS.txt FONTS_DIR [-rsbucp]\n\nOptional parameters create images in addition to an unmodified base image for each word in each font\n-r: create images that are rotated slightly CW and CCW\n-s: create images that are skewed slightly left and right\n-b: create images with a slight gaussian blur\n-u: create images with an underline\n-c: create images with a complex transformation composed of skewing and blurring\n-p: removes all punctuation from words\n"

if len(argv) < 3 or len(argv) > 4:
    print(USAGE)
    exit()

modifications = set(argv[3].strip('-')) if len(argv) == 4 else set()
do_rotate = 'r' in modifications
do_skew = 's' in modifications
do_blur = 'b' in modifications
do_underline = 'u' in modifications
do_complex = 'c' in modifications
do_remove_punctuation = 'p' in modifications

corpus_fp = argv[1]
with open(corpus_fp, 'rt') as corpus_file: corpus = corpus_file.read()
if do_remove_punctuation:
    words = set([sub(r'[^\w\s]', '', word, UNICODE) for word in corpus.split()])
else:
    words = set(corpus.split())

font_dir = argv[2]
font_fps = list(iglob(font_dir + '/*.ttf'))
font_names = [font_fp.split('/')[-1][:-4] for font_fp in font_fps]

output_dir = 'output/'
makedirs(output_dir, exist_ok=True)

print('\nFonts (%d): %s' % (len(font_names), font_names))
print('\nWords (%d): %s\n' % (len(words), list(words)))

for font_fp, font_name in zip(font_fps, font_names):
    print('Generating pictures for \'%s\'...' % font_name)

    for word in words:
        img = create_base_img(word, font_fp, dim=BASE_IMG_DIM, pos=TEXT_POS, font_size=FONT_SIZE, fill=BLACK, bg=WHITE)
        img_fp = output_dir + '/' + word + '.' + font_name + '.png'
        
        trim_ = lambda im: trim(im, BORDER)
        img = apply_modification_and_save(img, img_fp, 'trim', trim_, ret=True)

        if do_rotate:
            rot_ccw = lambda im: rotate(im, ROTATE_ANGLE)
            apply_modification_and_save(img, img_fp, 'rot_ccw', rot_ccw)

            rot_cw = lambda im: rotate(im, -ROTATE_ANGLE)
            apply_modification_and_save(img, img_fp, 'rot_cw', rot_cw)
        
        if do_skew:
            skew_r = lambda im: skew(im, SKEW_ANGLE)
            apply_modification_and_save(img, img_fp, 'skew_r', skew_r)
            
            skew_l = lambda im: skew(im, -SKEW_ANGLE)
            apply_modification_and_save(img, img_fp, 'skew_l', skew_l)
        
        if do_blur:
            blur_ = lambda im: blur(im, BLUR_RADIUS)
            apply_modification_and_save(img, img_fp, 'blur', blur_)

        if do_underline:
            ul = lambda im: underline(im, BORDER, FONT_SIZE)
            apply_modification_and_save(img, img_fp, 'ul', ul)
        
        if do_complex:
            skew_r_blur = lambda im: blur(skew(im, SKEW_ANGLE), BLUR_RADIUS)
            apply_modification_and_save(img, img_fp, 'skew_r_blur', skew_r_blur)

            skew_l_blur = lambda im: blur(skew(im, -SKEW_ANGLE), BLUR_RADIUS)
            apply_modification_and_save(img, img_fp, 'skew_l_blur', skew_l_blur)

num_mods = 1 + (2 * do_rotate) + (2 * do_skew) + (1 * do_blur) + (1 * do_underline) + (2 * do_complex)
num_pics = len(font_names) * len(words) * num_mods
print('\n%d pictures output to \'%s\'\n' % (num_pics, output_dir))

