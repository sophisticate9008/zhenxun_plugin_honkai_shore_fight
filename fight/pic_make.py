from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from zhenxun.configs.path_config import FONT_PATH
# font_path = "D:/05.code/01.python_code/zhenxun_bot/resources/font/HYWenHei-85W.ttf"
# Assuming IMAGE_PATH and FONT_PATH are predefined global variables


def image_add_text(txts: list, text_color=(255, 0, 0), text_size=13) -> bytes:
    img_back = Image.new("RGB", (510, (len(txts) * 14)), (255, 255, 255))
    fight_ttf = str(FONT_PATH / "HYWenHei-85W.ttf")

    # Create a drawing context
    draw = ImageDraw.Draw(img_back)
    fontStyle = ImageFont.truetype(fight_ttf, text_size, encoding="utf-8")

    # Draw each line of text
    for j, text in enumerate(txts):
        draw.text((0, j * 14), text, text_color, font=fontStyle)

    return img_to_bytes(img_back)


def img_to_bytes(img: Image.Image) -> bytes:
    """
    Converts the given image to a BytesIO stream for in-memory storage.
    """
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)  # Reset pointer to the start of the BytesIO stream
    return buf.getvalue()



