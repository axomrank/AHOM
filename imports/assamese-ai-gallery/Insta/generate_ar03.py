import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

bg_path = "/home/angsuman/.gemini/antigravity/brain/1652d2c9-3296-4a37-8023-eb652c6dfc56/ar03_bg_1_1791547862893.jpg"
out_dir = "/home/angsuman/extra_spac/Assam_Data/Insta/AR03"
os.makedirs(out_dir, exist_ok=True)

# Load fonts
try:
    font_brand = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf", 25)
    font_large = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSerifBengali-Bold.ttf", 65) # Serif for the elegant look
    font_medium = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf", 40)
    font_small = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf", 30)
except Exception as e:
    print("Font error:", e)
    font_brand = ImageFont.load_default()
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

slides_data = [
    {
        "headline": "আপুনি তিনিটা বিহুৰ\nপাৰ্থক্য ক'ব পাৰেনে?",
        "body": "জানিবলৈ ছ্ৱাইপ কৰক,\nতাৰ পিছত অনুশীলন কৰক।"
    },
    {
        "headline": "ব'হাগ / ৰঙালী বিহু",
        "body": "এপ্ৰিলৰ মাজভাগত উদযাপিত হয়।\nই অসমীয়া নৱবৰ্ষ আৰু বসন্ত ঋতুক চিহ্নিত কৰে।"
    },
    {
        "headline": "কাতি / কঙালী বিহু",
        "body": "অক্টোবৰৰ মাজভাগত পালন কৰা হয়।\nশস্যৰ বাবে বন্তি প্ৰজ্বলন আৰু প্ৰাৰ্থনা ইয়াৰ শান্ত স্বভাৱৰ মূল।"
    },
    {
        "headline": "মাঘ / ভোগালী বিহু",
        "body": "জানুৱাৰীৰ মাজভাগত উদযাপিত হয়।\nই শস্য চপোৱা, সামূহিক ভোজ আৰু মেজিৰ জুইৰ সৈতে জড়িত।"
    },
    {
        "headline": "অনুশীলনৰ প্ৰশ্ন",
        "body": "কোনটো বিহু অসমীয়া নৱবৰ্ষৰ সৈতে জড়িত?\n\nক. মাঘ    খ. কাতি    গ. ব'হাগ    ঘ. এটাও নহয়\n\nউত্তৰ: গ. ব'হাগ"
    },
    {
        "headline": "এই তুলনাটো\nচেভ কৰক।",
        "body": "AxomRank ত আৰু অধিক অসমীয়া\nসাধাৰণ জ্ঞানৰ অনুশীলন কৰক।\nলিংক বায়'ত আছে।"
    }
]

brand_color = '#5c141d'
text_color = '#2c2c2c'

for i, data in enumerate(slides_data):
    # Base image
    img = Image.open(bg_path).convert('RGB')
    img = img.resize((1080, 1350), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    
    # 1. Branding (Top center)
    brand_text = "AXOMRANK"
    bbox = draw.textbbox((0,0), brand_text, font=font_brand)
    w = bbox[2] - bbox[0]
    draw.text(((1080 - w)/2, 60), brand_text, font=font_brand, fill=brand_color)
    
    # Line below branding
    draw.line(((1080/2 - 40, 100), (1080/2 + 40, 100)), fill=brand_color, width=3)
    
    # 2. Headline (Top) - Align Center
    lines = data['headline'].split('\n')
    y_text = 150
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_large)
        w = bbox[2] - bbox[0]
        draw.text(((1080 - w)/2, y_text), line, font=font_large, fill=brand_color)
        y_text += 85
        
    # 3. Body text (Lower middle / bottom) - Align Center
    lines = data['body'].split('\n')
    y_body = 1050
    if i == 4: # Push practice question up slightly
        y_body = 950 
        
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font_medium)
        w = bbox[2] - bbox[0]
        draw.text(((1080 - w)/2, y_body), line, font=font_medium, fill=text_color)
        y_body += 60
        
    # 4. Slide Number (Bottom right)
    slide_indicator = f"{i+1}/6"
    draw.text((950, 1250), slide_indicator, font=font_small, fill=brand_color)
    
    out_path = os.path.join(out_dir, f"ar03_slide_{i+1}.png")
    img.save(out_path)
    print(f"Saved {out_path}")

