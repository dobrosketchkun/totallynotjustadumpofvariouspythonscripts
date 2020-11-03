'''
Makes jpegs from 16 bit TEM tifs
'''

from PIL import Image
from os import listdir, remove
from os.path import isfile, join
from tqdm import tqdm

import numpy as np
import imageio

mypath= './some_folder/'

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for file in tqdm(onlyfiles):
    try:
        img = imageio.imread(mypath + file)
        imageio.imwrite(mypath + file.split('.')[0] + '.jpg', img)
    except:
        print(file)
