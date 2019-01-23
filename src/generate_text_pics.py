# inspired by https://blogs.dropbox.com/tech/2017/04/creating-a-modern-ocr-pipeline-using-computer-vision-and-deep-learning/
from sys import argv
from glob import iglob
from os import makedirs
from re import sub, UNICODE
from utils import break_token_into_lines, create_base_img, trim, rotate, blur, skew, underline, apply_modification_and_save
from PIL import Image, ImageDraw, ImageFont


BASE_IMG_DIM = (1000, 1000)
TEXT_POS = (15,15)
FONT_SIZE = 25
BORDER = 10

ROTATE_ANGLE = 5
SKEW_ANGLE = 15
BLUR_RADIUS = 2

BLACK = 0
WHITE = 255

USAGE = "\nUSAGE:  python generate_text_pics.py [-cwspa] CORPUS.txt FONTS_DIR [-rsbucp]\n\nOptional parameters at the beginning of the command specify which tokens you would like to create (default is -w):\n-c: create images of the characters in the corpus\n-w: create images of the words in the corpus\n-s: create images of the sentences in the corpus\n-p: create images of the paragraphs in the corpus\n-a: create images of the entire corpus\n\nOptional parameters at the end of the command create images in addition to an unmodified base image for each word in each font\n-r: create images that are rotated slightly CW and CCW\n-s: create images that are skewed slightly left and right\n-b: create images with a slight gaussian blur\n-u: create images with an underline\n-c: create images with a complex transformation composed of skewing and blurring\n-p: removes all punctuation from words\n\nExample:\npython src/generate_text_pics.py -ws sample_text/lorem_ipsum.txt fonts/few/ -sb\n"

if len(argv) < 3 or len(argv) > 5:
    print(USAGE)
    exit()

# parse token types
token_types = set(argv[1][1:]) if argv[1][0] == '-' else set()
do_characters = 'c' in token_types
do_words = ('w' in token_types) or (len(token_types) == 0)
do_sentences = 's' in token_types
do_paragraphs = 'p' in token_types
do_all = 'a' in token_types

# parse image modifications
modifications = set(argv[-1][1:]) if argv[-1][0] == '-' else set()
do_rotate = 'r' in modifications
do_skew = 's' in modifications
do_blur = 'b' in modifications
do_underline = 'u' in modifications
do_complex = 'c' in modifications
do_remove_punctuation = 'p' in modifications

# load corpus
corpus_fp = argv[1] if not token_types else argv[2]
with open(corpus_fp, 'rt') as corpus_file: corpus = corpus_file.read()
# load font filepaths
font_dir = argv[2] if not token_types else argv[3]
font_fps = list(iglob(font_dir + '/**/*.ttf'))
font_names = [font_fp.split('/')[-1][:-4] for font_fp in font_fps]
print('\nFonts (%d): %s\n' % (len(font_names), font_names))

# break up corpus into tokens based on specified token types
tokens = set()
if do_all:
    tokens.add((corpus, 'all'))
paragraphs = set([(paragraph.strip(), 'paragraph') for paragraph in corpus.split('\n') if paragraph])
if do_paragraphs:
    tokens.update(paragraphs)
    print('Paragraphs (%d): %s' % (len(paragraphs), list(zip(*paragraphs))[0]))
sentences = set([(sentence, 'sentence') for paragraph, _ in paragraphs for sentence in paragraph.split('. ') if sentence])
if do_sentences:
    tokens.update(sentences)
    print('Sentences (%d): %s' % (len(sentences), list(zip(*sentences))[0]))
words = set([(word, 'word') for sentence, _ in sentences for word in sentence.split(' ') if word])
if do_remove_punctuation:
    words = set([(sub(r'[^\w\s]', '', word, UNICODE), label) for word, label in words])
if do_words:
    tokens.update(words)
    print('Words (%d): %s' % (len(words), list(zip(*words))[0]))
characters = set([(character, 'character') for word, _ in words for character in word])
if do_characters:
    tokens.update(characters)
    print('Characters (%d): %s' % (len(characters), list(zip(*characters))[0]))

# make output directory if necessary
output_dir = 'output/'
makedirs(output_dir, exist_ok=True)


for font_fp, font_name in zip(font_fps, font_names):
    print('\nGenerating pictures for \'%s\'...' % font_name)

    for token, token_type in tokens:

        if len(token) > 80:
            token = break_token_into_lines(token, 80)

        img = create_base_img(token, font_fp, dim=BASE_IMG_DIM, pos=TEXT_POS, font_size=FONT_SIZE, fill=BLACK, bg=WHITE)
        img_fp = output_dir + '/' + token_type + '.' + token[:20] + '.' + font_name + '.png'
        
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
            ul = lambda im: underline(im, FONT_SIZE, BORDER)
            apply_modification_and_save(img, img_fp, 'ul', ul)
        
        if do_complex:
            skew_r_blur = lambda im: blur(skew(im, SKEW_ANGLE), BLUR_RADIUS)
            apply_modification_and_save(img, img_fp, 'skew_r_blur', skew_r_blur)

            skew_l_blur = lambda im: blur(skew(im, -SKEW_ANGLE), BLUR_RADIUS)
            apply_modification_and_save(img, img_fp, 'skew_l_blur', skew_l_blur)


num_mods = 1 + (2 * do_rotate) + (2 * do_skew) + (1 * do_blur) + (1 * do_underline) + (2 * do_complex)
num_pics = len(font_names) * len(tokens) * num_mods
print('\n%d pictures output to \'%s\'\n' % (num_pics, output_dir))

