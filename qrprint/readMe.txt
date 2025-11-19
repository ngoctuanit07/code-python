qrprint \
  --data "https://fb.com/61577302259122" \
  --width-cm 7.439 \
  --height-mm 5.02 \
  --padding-mm 0.5 \
  --dpi 300 \
  --output label.png

Convert units helper (example):
  python -m qrprint.units 25.4 mm px --dpi 300

CLI example with cm and comma decimals (Windows PowerShell):
  cd d:\tools\dv
  python -m qrprint --data "https://fb.com/61577302259122" --width-cm "30,997" --height-cm "2,092" --padding-cm "0,5" --dpi 300 --output qrcode_fb_label.png
