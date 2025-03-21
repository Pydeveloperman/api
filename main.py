from fastapi import FastAPI, Query
from PIL import Image, ImageDraw, ImageFont
import io
from fastapi.responses import Response
import textwrap
import os

app = FastAPI()

@app.get("/text-to-image/")
def text_to_image(
    text: str = Query(..., title="Matn", description="Rasmga yoziladigan matn"),
    background: str = Query("backgraund.jpg", title="Fon rasmi", description="Fayl nomi")
):
    try:
        img = Image.open(background)  # Fonni yuklash
    except FileNotFoundError:
        return {"error": "Background image not found"}

    width, height = img.size
    draw = ImageDraw.Draw(img)

    # Shrift yuklash
    font_path = "f.ttf"
    if not os.path.exists(font_path):  # Agar shrift topilmasa
        font = ImageFont.load_default()
    else:
        font = ImageFont.truetype(font_path, 30)  # Boshlang‘ich shrift hajmi kichikroq qilindi

    # Matn uchun ajratilgan maydon koordinatalari (ramka ichida)
    frame_x1, frame_y1 = 50, 380  # Yuqori chap burchak
    frame_x2, frame_y2 = width - 50, height - 100  # Pastki o‘ng burchak
    frame_width = frame_x2 - frame_x1
    frame_height = frame_y2 - frame_y1

    # Shrift hajmini moslashtirish
    max_font_size = 30  # Kichikroq shrift hajmi
    while True:
        font = ImageFont.truetype(font_path, max_font_size)
        wrapped_text = textwrap.fill(text, width=35)  # Ko‘proq harf sig‘adigan qilib o‘zgartirildi
        
        # Matnning umumiy balandligini hisoblash
        total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in wrapped_text.split("\n")) + 8 * (wrapped_text.count("\n") + 1)

        if total_text_height < frame_height:
            break
        else:
            max_font_size -= 2  # Shriftni kichraytirish

    # Matnni ramka ichida o‘rtaga joylash
    text_y = frame_y1 + (frame_height - total_text_height) // 2

    for line in wrapped_text.split("\n"):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(((width - text_width) // 2, text_y), line, fill=(255, 255, 255), font=font)  # Oq matn
        text_y += bbox[3] - bbox[1] + 8  # Qatorlar orasidagi masofa kamaytirildi

    # Rasmni xotirada saqlash
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return Response(content=img_bytes.getvalue(), media_type="image/png")