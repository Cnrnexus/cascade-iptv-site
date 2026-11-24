#!/usr/bin/env python3
"""Generates the sample playlist, channel logos and a 60-day programme guide.

Every stream is a freely licensed work (Blender Foundation open movies, CC BY) or a
public player test stream. Guide entries name what the stream actually plays.
Run from the repository root:  python3 tools/gen_sample.py
"""
import datetime as dt, os
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw, ImageFont

BASE = "https://cnrnexus.github.io/cascade-iptv-site/test"
G_FILMS, G_LIVE, G_TEST = "Blender open movies (CC BY)", "Live samples", "Player test streams"
# id, name, group, initials, colour, block minutes, description, url
CH = [
 ("bbb", "Big Buck Bunny", G_FILMS, "BB", "#2E7D32", 60, "A gentle giant rabbit takes on three mischievous rodents. Blender Foundation open movie (2008).",
  "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"),
 ("ed", "Elephants Dream", G_FILMS, "ED", "#6A1B9A", 60, "Two characters explore a strange machine world. The first Blender open movie (2006).",
  "https://playertest.longtailvideo.com/adaptive/elephants_dream_v4/index.m3u8"),
 ("sintel", "Sintel", G_FILMS, "SI", "#AD1457", 60, "A young woman searches for her lost dragon companion. Blender Foundation open movie (2010).",
  "https://storage.googleapis.com/shaka-demo-assets/sintel-fmp4-aes/master.m3u8"),
 ("tos", "Tears of Steel", G_FILMS, "TS", "#4527A0", 60, "Scientists in a future Amsterdam try to save the world from robots. Blender Foundation open movie (2012).",
  "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel.ism/.m3u8"),
 ("tossub", "Tears of Steel (subtitles)", G_FILMS, "TS", "#283593", 60, "Tears of Steel with several subtitle languages, for trying the subtitle menu.",
  "https://demo.unified-streaming.com/k8s/features/stable/video/tears-of-steel/tears-of-steel-multiple-subtitles.ism/.m3u8"),
 ("live", "Tears of Steel Live", G_LIVE, "TL", "#1565C0", 120, "A continuous live loop of Tears of Steel with an on-screen clock.",
  "https://demo.unified-streaming.com/k8s/live/stable/live.isml/.m3u8"),
 ("bbblive", "Big Buck Bunny Live", G_LIVE, "BL", "#00695C", 120, "A continuous live loop of Big Buck Bunny.",
  "https://cph-p2p-msl.akamaized.net/hls/live/2000341/test/master.m3u8"),
 ("livemark", "Live with programme markers", G_LIVE, "LM", "#EF6C00", 120, "A live test loop that carries programme break markers.",
  "https://demo.unified-streaming.com/k8s/live/stable/scte35.isml/.m3u8"),
 ("bipbop", "Apple Test Stream", G_TEST, "AT", "#C62828", 120, "Apple's adaptive bitrate test pattern with audible beeps.",
  "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_16x9/bipbop_16x9_variant.m3u8"),
 ("bipbopadv", "Apple Advanced Stream", G_TEST, "AA", "#37474F", 120, "Apple's advanced test stream with several audio and subtitle tracks.",
  "https://devstreaming-cdn.apple.com/videos/streaming/examples/img_bipbop_adv_example_fmp4/master.m3u8"),
 ("bipbophevc", "Apple HEVC Stream", G_TEST, "AH", "#4E342E", 120, "Apple's HEVC (H.265) test stream.",
  "https://devstreaming-cdn.apple.com/videos/streaming/examples/bipbop_adv_example_hevc/master.m3u8"),
]

def font(size):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        if os.path.exists(p): return ImageFont.truetype(p, size)
    return ImageFont.load_default()

os.makedirs("test/logos", exist_ok=True)
for cid, name, group, ini, colour, mins, desc, url in CH:
    im = Image.new("RGB", (256, 256), colour)
    d = ImageDraw.Draw(im); f = font(112)
    x0, y0, x1, y1 = d.textbbox((0, 0), ini, font=f)
    d.text(((256 - (x1 - x0)) / 2 - x0, (256 - (y1 - y0)) / 2 - y0), ini, fill="white", font=f)
    im.save(f"test/logos/{cid}.png", optimize=True)

with open("test/cascade-test.m3u", "w", newline="\n") as f:
    f.write(f'#EXTM3U url-tvg="{BASE}/epg.xml"\n')
    for cid, name, group, ini, colour, mins, desc, url in CH:
        f.write(f'#EXTINF:-1 tvg-id="sample.{cid}" tvg-name="{name}" tvg-logo="{BASE}/logos/{cid}.png" group-title="{group}",{name}\n{url}\n')

start = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0) - dt.timedelta(days=1)
end = start + dt.timedelta(days=61)
fmt = lambda t: t.strftime("%Y%m%d%H%M%S +0000")
with open("test/epg.xml", "w", newline="\n") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<tv generator-info-name="Cascade sample guide">\n')
    for cid, name, *_ in CH:
        f.write(f'  <channel id="sample.{cid}"><display-name>{escape(name)}</display-name></channel>\n')
    for cid, name, group, ini, colour, mins, desc, url in CH:
        t = start
        while t < end:
            n = t + dt.timedelta(minutes=mins)
            f.write(f'  <programme start="{fmt(t)}" stop="{fmt(n)}" channel="sample.{cid}"><title>{escape(name)}</title><desc>{escape(desc)}</desc></programme>\n')
            t = n
    f.write('</tv>\n')
print(len(CH), "channels;", os.path.getsize("test/epg.xml") // 1024, "KB guide")
