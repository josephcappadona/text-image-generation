A library to generate pictures of text for the purposes of training machine learning models. Inspired by [this Dropbox blog post on building an OCR pipeline](https://blogs.dropbox.com/tech/2017/04/creating-a-modern-ocr-pipeline-using-computer-vision-and-deep-learning/).

##Usage
```
python generate_text_pics.py CORPUS.txt FONTS_DIR [-rsbucp]

Optional parameters create images in addition to an unmodified base image for each word in each font
-r: create images that are rotated slightly CW and CCW
-s: create images that are skewed slightly left and right
-b: create images with a slight gaussian blur
-u: create images with an underline
-c: create images with a complex transformation composed of skewing and blurring
-p: removes all punctuation from words
```

##Example
```
python src/generate_text_pics.py sample_text/lorem_ipsum.txt fonts/some/ -sbc
```
