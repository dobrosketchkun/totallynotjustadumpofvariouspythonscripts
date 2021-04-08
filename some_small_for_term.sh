# Count Files in Directory on Linux

ls /some/folder/ | wc -l

##################################






#####################
# ffmpeg section    #
#####################

# adding silent audio
ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i input.mp4 -c:v copy -c:a aac -shortest output.mp4

# cut from ss to t
ffmpeg -i input.mp4 -ss 00:00:06 -t 00:00:26 cut.mp4

# video to frames
ffmpeg -i input.mp4 frames/out-%03d.jpg

# from frames to video
ffmpeg -i frames/out-%03d.jpg -c:v libx264 -vf fps=29.97 -pix_fmt yuv420p output.mp4

# lighter video
ffmpeg -i input.mp4 -c:v libx264 -crf 18 -preset veryslow -c:a copy output.mp4

# loop video through audio

ffmpeg  -stream_loop -1 -i input.mp4 -i input.mp3 -shortest -map 0:v:0 -map 1:a:0 -y output.mp4
