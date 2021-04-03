# Count Files in Directory on Linux

ls /some/folder/ | wc -l

##################################






#####################
# ffmpeg section    #
#####################

# adding silent audio
ffmpeg -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -i input.mp4 -c:v copy -c:a aac -shortest output.mp4
