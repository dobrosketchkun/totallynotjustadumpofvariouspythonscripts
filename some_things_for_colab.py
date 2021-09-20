###########################
'''
Shows a video in colab
'''

from IPython.display import HTML
from base64 import b64encode
mp4 = open(movie_name,'rb').read()
data_url = "data:video/mp4;base64," + b64encode(mp4).decode()
HTML("""
<video width=400 controls>
      <source src="%s" type="video/mp4">
</video>
""" % data_url)

####################
'''
Connect gdrive to clab
'''

from google.colab import drive
drive.mount('/content/drive')

#####################
'''
Download bunch of files in colab /content/ temporary drive
'''


#make a directory (mb with subdirectory)
for p in ["/content/datasets/", '/content/datasets/custom']:
  try:
    os.mkdir(p)
  except:
    pass


import os
ids = [] #list of IDs of files 

for id in ids:
  print('Downloading', id)
  os.system('gdown --id ' + id)

#####################
'''
Display multiple images.
'''
from IPython.display import Image, display
display(Image('a.png', width=300))
display(Image('b.png', height=300))

#####################
'''
inline plot 
'''

%matplotlib inline
from pylab import rcParams
import matplotlib.pyplot as plt
rcParams['figure.figsize'] = 20 , 10

#####################
'''
Autorun form
'''
#@title Attribute. { run: "auto" }


#####################
'''
Dowload file
'''

from google.colab import files
files.download('file.txt') 

#####################
'''
Restart a runtime in the code
'''

#@title ← Press this button to restart runtime. Ignore the <i>session crashed</i> message and run the next cell 
import os
os.kill(os.getpid(), 9)
