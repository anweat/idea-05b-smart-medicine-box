#!/bin/zsh
# 把 renders/v3/anim/<mode>/f_####.png 合成 MP4（展示页用）和 GIF（交付 / 汇报用）
# 用法：tools/v3/encode_anim.sh pour sweep load
cd "$(dirname "$0")/../../renders/v3/anim" || exit 1
for m in "$@"; do
  ffmpeg -y -loglevel error -framerate 30 -i "$m/f_%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 24 -movflags +faststart "$m.mp4"
  ffmpeg -y -loglevel error -framerate 30 -i "$m/f_%04d.png" \
    -vf "fps=15,scale=640:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=128[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" "$m.gif"
  echo "ENC $m $(du -h "$m.mp4" | cut -f1) $(du -h "$m.gif" | cut -f1)"
done
