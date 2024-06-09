# wsacro_scoring
ffmpeg -ss 00:00:40 -to 00:02:54 -i GX010612.MP4 -vcodec copy -acodec copy output2.MP4

ffmpeg -i GH010420.mp4 -vf scale=1920:1080 -c:v libx264 -crf 20 -preset slow GH010420_1080p.mp4
ffmpeg -i GX010612.mp4 -vf scale=1920:1080 -c:v libx264 -crf 20 -preset slow GX010612_1080p.mp4

ffmpeg -i GH010420.MP4 -map 0 -map -0:a -c copy GH010420_MUTED.MP4
ffmpeg -i GX010612.MP4 -map 0 -map -0:a -c copy GX010612_MUTED.MP4

1) Concatenate a list of videos into one

ffmpeg -f concat -safe 0 -i tojoin.txt -c copy output.mp4

// Format of tojoin.txt:
file 'file0.MP4'
file 'file1.MP4'
file 'etc..

2) Scale down 4k video to

// 2.7k / 2704p
ffmpeg -i output.mp4 -vf scale=2704:1520 -c:v libx264 -crf 20 -preset slow smaller_2704p.mp4

// 1440p
ffmpeg -i output.mp4 -vf scale=1920:1440 -c:v libx264 -crf 20 -preset slow smaller_1440p.mp4

// 1080p
ffmpeg -i output.mp4 -vf scale=1920:1080 -c:v libx264 -crf 20 -preset slow smaller_1080p.mp4

// 720p
ffmpeg -i output.mp4 -vf scale=1280:720 -c:v libx264 -crf 20 -preset slow smaller_720p.mp4

convert.py -s 00:00:10 -c 00:00:37 -f flysight_data/stockholm3.csv -fly 2 -v ../../GH010420.MP4 -o 0_r1.mp4


score_round -r round_list.csv -c -s -re