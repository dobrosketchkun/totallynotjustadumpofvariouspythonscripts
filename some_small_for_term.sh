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

# cut video for telegram
ffmpeg -ss 00:00:00 -to 00:00:01 -i "input.mp4" -vf format=yuv420p -preset veryslow output.mp4 -y

# cut video for telegram with hardsubs
ffmpeg -ss 00:00:00 -to 00:00:01 -copyts -i "input.mkv"  -vf "format=yuv420p,subtitles='input.mkv'" -ss 00:00:00 -preset veryslow output.mp4 -y
ffmpeg --ss 00:00:00 -to 00:00:01 -copyts -i "input.mkv"   -filter_complex "ass='input.ass'" -ss 00:00:00 -preset veryslow output.mp4 -y

# make a "gif" for telegram
ffmpeg -i input.mp4 -flags +global_header -movflags faststart -c:v libx264 -profile:v high -bf 0 -copyts -avoid_negative_ts disabled -correct_ts_overflow 0 -pix_fmt yuv420p -color_primaries bt709 -color_trc iec61966_2_1 -colorspace bt470bg -color_range tv -video_track_timescale 24000/1 -vsync passthrough -qp 18 -preset veryslow -lavfi scale=if(gt(iw\,ih)\,min(448\,floor((iw+1)/2)*2)\,-2):if(gt(iw\,ih)\,-2\,min(448\,floor((ih+1)/2)*2)):out_color_matrix=bt601:out_range=tv:flags=accurate_rnd+full_chroma_inp+full_chroma_int+bicublin -an output.mp4

# concatenate multiple files
ffmpeg -i "concat:audio1.mp3|audio2.mp3|audio3.mp3" output.mp3

# split a file into segments of some length (in seconds)
ffmpeg -i input.mp3 -f segment -segment_time 60 -c copy output_%03d.mp3
