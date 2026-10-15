import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

bg_dir = "/home/angsuman/.gemini/antigravity/brain/1652d2c9-3296-4a37-8023-eb652c6dfc56"
out_dir = "/home/angsuman/extra_spac/Assam_Data/Insta/AR02"
os.makedirs(out_dir, exist_ok=True)

try:
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf", 70)
    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf", 45)
    font_brand = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf", 35)
except Exception as e:
    print("Font error:", e)
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_brand = ImageFont.load_default()

slides_data = [
    {
        "bg": "ar02_bg_1_1791543420469.jpg",
        "headline": "আজি পঢ়িবলৈ কেৱল এক ঘণ্টাহে আছে নেকি?",
        "body": "জানিবলৈ ছ্ৱাইপ কৰক, তাৰ পিছত অনুশীলন কৰক।"
    },
    {
        "bg": "ar02_bg_2_1791543432877.jpg",
        "headline": "১০ মিনিট: মনত পেলাওক",
        "body": "আপোনাৰ টোকাবহী বন্ধ কৰক। কালিৰ পৰা যি মনত আছে সেয়া লিখক। খালী ঠাইবোৰত চক্ৰ আঁকক।"
    },
    {
        "bg": "bg_3_auto", # wait, what's the actual filename?
        "headline": "২০ মিনিট: এটা দুৰ্বল বিষয়",
        "body": "শেহতীয়া পৰীক্ষাত আপুনি ভুল কৰা এটা ধাৰণা বাছক। ইয়াৰ ব্যাখ্যা পঢ়ক আৰু এটা উদাহৰণৰ মাজেৰে কাম কৰক।"
    },
    {
        "bg": "bg_4_auto",
        "headline": "২০ মিনিট: অনুশীলন",
        "body": "সেই বিষয়টোৰ ওপৰত সৰু প্ৰশ্নৰ ছেট এটা সমাধান কৰক। চেষ্টা কৰাৰ পিছত উত্তৰৰ ব্যাখ্যামূহ পৰীক্ষা কৰক।"
    },
    {
        "bg": "bg_5_auto",
        "headline": "১০ মিনিট: পুনৰীক্ষণ",
        "body": "এটা ভুল আৰু এটা শুদ্ধকৰণ লিখক। আপোনাৰ টোকাবহী বন্ধ কৰাৰ আগতে কাইলৈৰ প্ৰথম বিষয়টো ঠিক কৰক।"
    },
    {
        "bg": "bg_6_auto",
        "headline": "আপোনাৰ এঘণ্টীয়া অধ্যয়নৰ পৰিকল্পনা চেভ কৰক।",
        "body": "AxomRank ত অনুশীলন কৰক। লিংক বায়'ত আছে।"
    }
]

import glob
bgs = sorted(glob.glob(f"{bg_dir}/ar02_bg_*.jpg"))
for i, bg_path in enumerate(bgs):
    img = Image.open(bg_path)
    # Ensure it's 1080x1350
    img = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    
    data = slides_data[i]
    color_text = '#292929' if i < 5 else '#FFFFFF'
    brand_color = '#80151A' if i < 5 else '#FFFFFF'
    
    # Axomrank line top left
    draw.text((80, 80), "AxomRank - Study Planner", font=font_brand, fill=brand_color)
    
    # Headline
    headline_wrap = textwrap.fill(data['headline'], width=22)
    draw.text((80, 300), headline_wrap, font=font_large, fill=color_text)
    
    # Body
    body_wrap = textwrap.fill(data['body'], width=38)
    draw.text((80, 600), body_wrap, font=font_medium, fill=color_text)
    
    out_path = os.path.join(out_dir, f"ar02_slide_{i+1}.png")
    img.save(out_path)
    print(f"Saved {out_path}")
