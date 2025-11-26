'''
Pads image to a square
'''


from PIL import Image, ImageOps
from os import listdir, remove
from os.path import isfile, join
import time
from tqdm import tqdm

finalsize = (1024, 1024)

mypath = './archillect/'
newpath = './archillect_paded/'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
removing = []


for file in tqdm(onlyfiles):
    im = Image.open(mypath + file)
    desired_size = max(im.size)

    old_size = im.size  # old_size[0] is in (width, height) format

    ratio = float(desired_size)/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    # use thumbnail() or resize() method to resize the input image

    # thumbnail is a in-place operation

    # im.thumbnail(new_size, Image.ANTIALIAS)

    im = im.resize(new_size, Image.ANTIALIAS)
    # create a new image and paste the resized on it

    new_im = Image.new("RGB", (desired_size, desired_size))
    new_im.paste(im, ((desired_size-new_size[0])//2,
                        (desired_size-new_size[1])//2))


    
    im1 = new_im.resize(finalsize) 
    # print('Saving ', file)
    im1.save(newpath + file,"JPEG")
    im1.save(newpath + file)
