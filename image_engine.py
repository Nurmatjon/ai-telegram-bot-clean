from PIL import Image, ImageDraw, ImageFont
from themes import THEMES

# =====================================================
# GRADIENT FON
# =====================================================
def draw_vertical_gradient(img, top_color, bottom_color):
    width, height = img.size
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b))


# =====================================================
# MATN KENGligini ANIQLASH (Pillow 10+)
# =====================================================
def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]


# =====================================================
# JUSTIFY (chap + o‘ng tekislash)
# =====================================================
def draw_justified_text(draw, text, font, x, y, max_width, line_height, fill):
    if not text:
        return y

    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if text_width(draw, test_line, font) <= max_width:
            current_line.append(word)
        else:
            lines.append(current_line)
            current_line = [word]

    if current_line:
        lines.append(current_line)

    for i, line_words in enumerate(lines):
        if i == len(lines) - 1 or len(line_words) == 1:
            draw.text((x, y), " ".join(line_words), font=font, fill=fill)
        else:
            words_w = sum(text_width(draw, w, font) for w in line_words)
            space = (max_width - words_w) // (len(line_words) - 1)
            cx = x
            for w in line_words:
                draw.text((cx, y), w, font=font, fill=fill)
                cx += text_width(draw, w, font) + space
        y += line_height

    return y


# =====================================================
# ASOSIY RASM GENERATOR (FINAL)
# =====================================================
def generate_image_block(data: dict, theme: str, filename: str):
    # 🔹 Telegram uchun ENG TO‘G‘RI FORMAT
    W, H = 1080, 1350  # 4:5
    colors = THEMES.get(theme, THEMES["pul"])

    # Gradient fon
    img = Image.new("RGB", (W, H))
    draw_vertical_gradient(
        img,
        (15, 45, 80),   # yuqori rang
        (20, 120, 90)   # pastki rang
    )
    draw = ImageDraw.Draw(img)

    # Shrifts
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 64)   # qalin
        font_body = ImageFont.truetype("arial.ttf", 46)
        font_cta = ImageFont.truetype("arialbd.ttf", 48)    # qalin
        font_brand = ImageFont.truetype("arial.ttf", 34)
    except:
        font_title = font_body = font_cta = font_brand = ImageFont.load_default()

    x_margin = 100
    max_width = W - 2 * x_margin
    y = 200

    # -------- SARLAVHA --------
    y = draw_justified_text(
        draw,
        data.get("title", ""),
        font_title,
        x_margin,
        y,
        max_width,
        80,
        "white"
    )

    y += 40

    # -------- ASOSIY MATN --------
    y = draw_justified_text(
        draw,
        data.get("body", ""),
        font_body,
        x_margin,
        y,
        max_width,
        60,
        colors["body"]
    )

    y += 50

    # -------- SAVOL / CTA --------
    y = draw_justified_text(
        draw,
        data.get("question", ""),
        font_cta,
        x_margin,
        y,
        max_width,
        70,
        colors["cta"]
    )

    # -------- BRANDING --------
    draw.text(
        (x_margin, H - 80),
        "Daromad Yo‘li",
        font=font_brand,
        fill=colors["cta"]
    )

    img.save(filename)
    return filename
