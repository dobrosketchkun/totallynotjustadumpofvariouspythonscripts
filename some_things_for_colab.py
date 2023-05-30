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
Shows a video in colab as a loop
'''

from IPython.display import HTML
from base64 import b64encode

video_path = '/path/to/your/video.mp4'

video_file = open(video_path, 'rb').read()
video_base64 = b64encode(video_file).decode()
data_url = "data:video/mp4;base64," + video_base64
html_code = """
<video width=400 controls autoplay>
    <source src="%s" type="video/mp4">
    Your browser does not support the video tag.
</video>

<script>
  var video = document.querySelector('video');
  video.addEventListener('ended', function () {
      video.currentTime = 0;
      video.play();
  });
</script>
""" % data_url

HTML(html_code)

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


#####################
'''
Allow text wrapping in generated output: https://stackoverflow.com/a/61401455
'''
from IPython.display import HTML, display

def set_css():
  display(HTML('''
  <style>
    pre {
        white-space: pre-wrap;
    }
  </style>
  '''))
get_ipython().events.register('pre_run_cell', set_css)


#####################
'''
Tesla P100-PCIE-16GB, 16280 MiB, 16280 MiB
'''

!nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader

#####################
'''
Frees GPU Memory, but it's very hacky, so
'''

# https://www.kaggle.com/getting-started/140636
from numba import cuda
def free_gpu_memory():
    cuda.select_device(0)
    cuda.close()
    cuda.select_device(0)

#####################
'''
Conditional tqdm
'''

from tqdm import tqdm

def tqdm_vervose(itterator, conditional):
    if not conditional:
        return itterator
    else:
        return tqdm(itterator)
 
for _ in tqdm_vervose(itterator=[1,2,3,4,5], conditional=True):
      do_something(_)

#####################
'''
Makes gdown work again
'''

!pip install --upgrade --no-cache-dir gdown

#####################
'''
Generates 24h silence audio file to play to force colab not to stop working
'''
#@title 1. Keep this tab alive to prevent Colab from disconnecting you { display-mode: "form" }

#@markdown Press play on the music player that will appear below:
from IPython.display import Audio, display,clear_output

!ffmpeg -f lavfi -i anullsrc=r=11025:cl=mono -t 86400 -acodec aac 24hsil.m4a -y
clear_output()
display(Audio('/content/24hsil.m4a'))

#####################


