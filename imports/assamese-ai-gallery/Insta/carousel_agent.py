import os
import textwrap
import openpyxl
from PIL import Image, ImageDraw, ImageFont
from google_antigravity import Agent, LocalAgentConfig

def get_font(size):
    try:
        # Try finding Lohit Assamese for Assamese support
        return ImageFont.truetype("/usr/share/fonts/truetype/lohit-assamese/Lohit-Assamese.ttf", size)
    except:
        return ImageFont.load_default()

def create_carousel_slide(post_id, slide_num, role, headline, body, output_dir):
    # Instagram Carousel 4:5 Aspect Ratio
    img = Image.new('RGB', (1080, 1350), color='#F7F2EC') # Warm Ivory background
    draw = ImageDraw.Draw(img)
    
    font_large = get_font(60)
    font_medium = get_font(40)
    
    # Draw Role & Slide Number (Brand color: Deep maroon #80151A)
    draw.text((100, 150), f"{role} - Slide {slide_num}", font=font_medium, fill='#80151A')
    
    # Draw Headline
    wrapped_headline = textwrap.fill(headline, width=30)
    draw.text((100, 300), wrapped_headline, font=font_large, fill='#292929')
    
    # Draw Body Copy
    wrapped_body = textwrap.fill(body, width=45)
    draw.text((100, 600), wrapped_body, font=font_medium, fill='#292929')
    
    os.makedirs(output_dir, exist_ok=True)
    img.save(os.path.join(output_dir, f"{post_id}_slide_{slide_num}.png"))

def main():
    if not os.environ.get("GEMINI_API_KEY"):
        print("Please set GEMINI_API_KEY to run the translation agent.")
        print("Run: export GEMINI_API_KEY='your-key'")
        return

    excel_path = '/home/angsuman/extra_spac/Assam_Data/Insta/AxomRank_Instagram_Carousel_Calendar_Oct-Dec_2026.xlsx'
    print(f"Loading {excel_path}...")
    wb = openpyxl.load_workbook(excel_path)
    sheet = wb['Slide Copy']
    
    # Initialize the Antigravity translation agent
    config = LocalAgentConfig(
        model="gemini-2.5-flash",
        system_instruction="You are a professional English to Assamese translator. Translate the provided Instagram carousel content to Assamese natively. Ensure high-quality, readable Assamese. DO NOT translate any English hashtags or UI labels, and output ONLY the translated text without extra formatting."
    )
    agent = Agent(config=config)
    
    output_dir = '/home/angsuman/extra_spac/Assam_Data/Insta/Assamese_Carousals'
    
    rows = list(sheet.iter_rows(values_only=True))
    
    # Skip header rows until we find the actual data
    data_started = False
    
    for row in rows:
        if not data_started:
            if row and row[0] == "Post ID":
                data_started = True
            continue
            
        if not row or not row[0]: 
            continue
            
        post_id = str(row[0])
        slide_num = str(row[1])
        role = str(row[2])
        headline_en = str(row[3]) if row[3] else ""
        body_en = str(row[4]) if row[4] else ""
        
        print(f"Translating {post_id} - Slide {slide_num}...")
        
        headline_asm = headline_en
        if headline_en and headline_en.lower() != "none":
            try:
                response = agent.run(f"Translate this headline to Assamese: {headline_en}")
                headline_asm = response.text.strip()
            except Exception as e:
                print(f"Headline Translation error on {post_id} s{slide_num}: {e}")
                
        body_asm = body_en
        if body_en and body_en.lower() != "none":
            try:
                response = agent.run(f"Translate this body copy to Assamese: {body_en}")
                body_asm = response.text.strip()
            except Exception as e:
                print(f"Body Translation error on {post_id} s{slide_num}: {e}")
                
        create_carousel_slide(post_id, slide_num, role, headline_asm, body_asm, output_dir)
        print(f"Successfully generated Assamese slide: {post_id} - Slide {slide_num}")

if __name__ == "__main__":
    main()
