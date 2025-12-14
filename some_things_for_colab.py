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
'''.

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
'''
Once you have loaded it, any cell run after this will give you the execution time of the cell.
'''
!pip install ipython-autotime
%load_ext autotime
# %unload_ext autotime # to unload

#####################
'''
Download a file with a progress line
'''

def download_file(url, folder_path, file_name=None):
    """Download a file from a given URL to a specified folder with an optional file name."""
    local_filename = file_name if file_name else url.split('/')[-1]
    local_filepath = os.path.join(folder_path, local_filename)

    # Stream download to handle large files
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size_in_bytes = int(r.headers.get('content-length', 0))
        block_size = 1024 # 1 Kibibyte
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
        with open(local_filepath, 'wb') as f:
            for data in r.iter_content(block_size):
                progress_bar.update(len(data))
                f.write(data)
        progress_bar.close()

    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    else:
        print(f"Downloaded {local_filename} to {folder_path}")

#####################
'''
Prepares a single grid of images
'''

from typing import List
from typing import List
from PIL import Image
import PIL

def make_image_grid(images: List[PIL.Image.Image], rows: int, cols: int, max_size: int = None) -> PIL.Image.Image:
    """
    Prepares a single grid of images. Useful for visualization purposes.
    
    :param images: A list of PIL Images to be arranged in a grid.
    :param rows: Number of rows in the grid.
    :param cols: Number of columns in the grid.
    :param max_size: The maximum size (width) for resizing the images. Both dimensions will be adjusted to maintain aspect ratios. If None, images are kept at their original sizes.
    :return: A single PIL Image representing the grid of resized images.
    """
    #####################
    def _create_grid_from_images(images: List[PIL.Image.Image], rows: int, cols: int) -> PIL.Image.Image:
        """
        Helper function to create a grid from a list of images.
        """
        w, h = images[0].size
        grid = Image.new("RGB", size=(cols * w, rows * h))

        for i, img in enumerate(images):
            grid.paste(img, box=(i % cols * w, i // cols * h))
        return grid
    #####################
    
    assert len(images) == rows * cols

    # If max_size is None, skip resizing and proceed with the original images
    if max_size is None:
        return _create_grid_from_images(images, rows, cols)

    # Determine the maximum width among all images
    max_width = max(img.width for img in images)

    # Calculate the scaling factor based on the maximum width
    scale_factor = max_size / max_width

    # Resize each image
    resized_images = []
    for img in images:
        width, height = img.size
        new_width = round(width * scale_factor)
        new_height = round(height * scale_factor)
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        resized_images.append(resized_img)

    return _create_grid_from_images(resized_images, rows, cols)


#####################
'''
Detects if the code is in the colab cell or not
'''

import sys 
def in_colab():
    return "google.colab" in sys.modules

#####################
'''
WinDirStat-like preview of what is happening on your gdrive
'''

# === GRADIO VERSION - Simple GDrive File/Folder Analyzer ===
%pip install gradio plotly pandas -q

import os
import gradio as gr
import plotly.express as px
import pandas as pd
from pathlib import Path
from collections import defaultdict

# Mount Google Drive
try:
    from google.colab import drive
    drive.mount('/content/drive')
    DEFAULT_ROOT = '/content/drive/MyDrive'
except:
    DEFAULT_ROOT = os.path.expanduser('~')

def format_size(size_bytes):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def scan_directory(root_path, progress=gr.Progress()):
    """Scan directory and return file data."""
    if not root_path or not os.path.isdir(root_path):
        return None, None, "Invalid path"
    
    files_data = []
    folder_sizes = defaultdict(int)
    
    progress(0, desc="Starting scan...")
    total_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                size = os.path.getsize(filepath)
                ext = Path(filename).suffix.lower() or '.no_ext'
                rel_path = os.path.relpath(filepath, root_path)
                parts = rel_path.split(os.sep)
                hierarchy = '/'.join(parts[:-1]) if len(parts) > 1 else '(root)'
                
                files_data.append({
                    'name': filename,
                    'size': size,
                    'size_fmt': format_size(size),
                    'ext': ext,
                    'path': filepath,
                    'parent': os.path.dirname(filepath),
                    'hierarchy': hierarchy
                })
                
                # Add to folder sizes
                folder_sizes[os.path.dirname(filepath)] += size
                total_files += 1
                
                if total_files % 200 == 0:
                    progress(0.5, desc=f"Scanned {total_files} files...")
                    
            except (OSError, PermissionError):
                pass
    
    progress(1, desc="Building visualization...")
    
    if not files_data:
        return None, None, None, "No files found"
    
    df = pd.DataFrame(files_data)
    
    # Limit treemap to top 500 largest files for performance
    # (too many files freezes the browser)
    df_treemap = df.nlargest(500, 'size').copy()
    
    # Create treemap with limited data
    fig = px.treemap(
        df_treemap,
        path=[px.Constant(os.path.basename(root_path) or 'Drive'), 'hierarchy', 'name'],
        values='size',
        color='ext',
        color_discrete_sequence=px.colors.qualitative.Bold,
        hover_data={'size_fmt': True, 'ext': True}
    )
    
    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Size: %{customdata[0]}<br>Type: %{customdata[1]}<extra></extra>',
        marker=dict(line=dict(width=1, color='#ddd')),
        textfont=dict(color='white'),
        textposition='middle center',
        insidetextfont=dict(size=14),
        texttemplate='%{label}'
    )
    
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(color='#333'),
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        showlegend=False
    )
    
    # Create files table (top 100 by size)
    top_files = df.nlargest(100, 'size')[['name', 'size_fmt', 'ext', 'parent']].copy()
    top_files.columns = ['Name', 'Size', 'Type', 'Location']
    
    # Create folders table
    folders_df = pd.DataFrame([
        {'Folder': k, 'Size': format_size(v)} 
        for k, v in sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:100]
    ])
    
    treemap_count = min(500, len(df))
    status = f"✅ {total_files} files scanned (showing top {treemap_count} in treemap)"
    return fig, top_files, folders_df, status

def run_scan(root_path, progress=gr.Progress()):
    fig, files_df, folders_df, status = scan_directory(root_path, progress)
    return fig, files_df, folders_df, status

# Build Gradio UI
with gr.Blocks(title="GDrive Analyzer") as app:
    
    gr.Markdown("## 📊 Google Drive Space Analyzer")
    
    with gr.Row():
        root_input = gr.Textbox(value=DEFAULT_ROOT, label="Root Path", scale=4)
        scan_btn = gr.Button("🔍 Scan", variant="primary", scale=1)
        status_text = gr.Textbox(label="Status", interactive=False, scale=2)
    
    with gr.Tabs():
        with gr.Tab("📊 Treemap"):
            treemap = gr.Plot(show_label=False)
        
        with gr.Tab("📁 Largest Files"):
            files_table = gr.Dataframe(
                headers=["Name", "Size", "Type", "Location"],
                show_label=False,
                max_height=700
            )
        
        with gr.Tab("📂 Largest Folders"):
            folders_table = gr.Dataframe(
                headers=["Folder", "Size"],
                show_label=False,
                max_height=700
            )
    
    scan_btn.click(
        fn=run_scan,
        inputs=[root_input],
        outputs=[treemap, files_table, folders_table, status_text]
    )

# Launch
app.launch(share=True)

#####################