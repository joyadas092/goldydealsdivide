import tempfile
from io import BytesIO
from openai import OpenAI
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# from playwright.async_api import async_playwright
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt
# from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv
import json


def env_float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def env_int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
apitoken=os.getenv('EARNKARO_API_TOKEN')
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.getenv("LOGO_PATH", os.path.join(script_dir, "logo.png"))
brand_banner_text = os.getenv("BRAND_BANNER_TEXT", "Join @LootsVault")
center_watermark_scale = env_float("CENTER_WATERMARK_SCALE", 0.60)
center_watermark_opacity = env_int("CENTER_WATERMARK_OPACITY", 20)
center_watermark_shadow_opacity = env_int("CENTER_WATERMARK_SHADOW_OPACITY", 25)
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Define a handler for the /start command
bot = Quart(__name__)
# bot.config['PROVIDE_AUTOMATIC_OPTIONS'] = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002365489797]  # Replace with the source channel ID
amazon_id = -1002385099278
flipkart_id = -1003066292672
meesho_id = -1002466670728
ajiomyntra_id = -1003928380634
zepto_id = -1003059572977
# cc_id = -1002078634799
# beauty_id = -1002046497963
private_channel = [-1002803694251]

BUDGET_CHANNEL_ID = -1003898460377

zepto_keywords=['jiomart','Amazon Fresh','blinkit','zepto','swiggy','bigbasket','Instamart','Flipkart minutes','instamart','Blinkit',
                'Zepto','Swiggy','flipkart minutes','minutes loot','ONDC','Zomato','Blinkit']
amazon_keywords = ['amzn', 'amazon', 'tinyurl','amazn']
flipkart_keywords = ['fkrt', 'flipkart', 'boat', 'croma', 'tatacliq', 'fktr', 'Boat', 'Tatacliq', 'noise', 'firebolt','fkart']
meesho_keywords = ['meesho', 'shopsy', 'msho','lehlah']
ajio_keywords = ['ajiio', 'myntr', 'xyxx', 'ajio', 'myntra', 'mamaearth', 'bombayshavingcompany', 'beardo', 'Beardo',
                 'Tresemme', 'themancompany', 'wow', 'nykaa',
                 'mCaffeine', 'mcaffeine', 'Bombay Shaving Company', 'BSC', 'TMC', 'foxtale',
                 'fitspire', 'PUER', 'foxtaleskin', 'fitspire', 'pueronline', 'plumgoodness', 'myglamm',
                 'himalayawellness', 'biotique', 'foreo', 'vega', 'maybelline', 'lorealparis',
                 'lakmeindia', 'clinique', 'thebodyshop', 'sephora', 'naturesbasket', 'healthandglow',
                 'colorbarcosmetics', 'sugarcosmetics', 'kamaayurveda', 'forestessentialsindia', 'derma', 'clovia',
                 'zandu', 'renee', 'bellavita']
# cc_keywords=['axis','hdfc','icici','sbm','sbi','credit','idfc','aubank','hsbc','Axis','Hdfc','Icici','Sbm','Sbi','Credit','Idfc','Aubank','Hsbc',
#             'AXIS','HDFC','ICICI','SBM','SBI','CREDIT','IDFC','AUBANK','HSBC']
# cc_keywords = ['Apply Now', 'Lifetime Free', 'Apply for', ' Lifetime free', 'Benifits', 'Apply here', 'Lifetime FREE',
#                'ELIGIBILITY', 'Myzone', 'Rupay', 'rupay', 'Complimentary', 'Apply from here', 'annual fee',
#                'Annual fee', 'joining fee']

shortnerfound = ['extp', 'bitli', 'bit.ly', 'bitly', 'bitili', 'biti','wishlink','bittli','cutt.ly','bilty','cuttli','bilty.co','bttly']

# tuple(amazon_keywords): amazon_id,
    # tuple(zepto_keywords):zepto_id,
keyword_to_chat_id = {
    tuple(amazon_keywords): amazon_id,
    tuple(flipkart_keywords): flipkart_id,
    tuple(meesho_keywords): meesho_id,
    tuple(ajio_keywords): ajiomyntra_id
}
BANNER_MESSAGES = {
    -1002049093974: "🔥Search @LootsVault ❤️‍🔥",  # Replace with actual channel ID
    -1002347373294: "💥 Search @LootsVault💥",
    -1002466670728: "🛍️ Search  @LootsVault 🛍️",
    -1002410844336: " 👗 Search @LootsVault 😉"
}
# =========================
# 📌 Silent Control
# =========================
silent_interval = 3   # Default: notify every 2nd post
post_counter = {}     # Track posts per target channel

def extract_link_from_text(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls[0] if urls else None


def tinycovert(text):
    unshortened_urls = {}
    urls = extract_link_from_text2(text)
    for url in urls:
        unshortened_urls[url] = tiny(url)
    for original_url, unshortened_url in unshortened_urls.items():
        text = text.replace(original_url, unshortened_url)
    return text


def tiny(long_url):
    url = 'http://tinyurl.com/api-create.php?url='

    response = requests.get(url + long_url)
    short_url = response.text
    return short_url


def extract_link_from_text2(text):
    # Regular expression pattern to match a URL
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls


def unshorten_url2(short_url):
    unshortener = UnshortenIt()
    shorturi = unshortener.unshorten(short_url)
    # print(shorturi)
    return shorturi


# async def unshorten_url(url):
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=True)
#             page = await browser.new_page()
#             await page.goto(url)
#             final_url = page.url
#             await browser.close()
#             return final_url
#     except Exception as e:
#         print(f"Error: {e}")
#         return None


def removedup(text):
    urls = re.findall(r"https?://\S+", text)
    unique_urls = []
    seen = set()

    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    # Remove duplicate URL lines
    lines = text.split("\n")
    cleaned_lines = []
    seen_urls = set()

    for line in lines:
        if any(url in line for url in unique_urls):
            # If the URL in the line is already seen, skip it
            url_in_line = next((url for url in unique_urls if url in line), None)
            if url_in_line and url_in_line in seen_urls:
                continue
            seen_urls.add(url_in_line)

        cleaned_lines.append(line)

    # Join cleaned lines back
    cleaned_text = "\n".join(cleaned_lines).strip()

    return cleaned_text


def get_font(size, bold=False):
    font_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        "arial.ttf",
    ]
    for font_file in font_candidates:
        try:
            return ImageFont.truetype(font_file, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def resolve_logo_path():
    if logo_path and os.path.exists(logo_path):
        return logo_path

    for filename in ("logo.png", "logo.jpg", "logo.jpeg", "lootsxpert_logo.png", "lootsxpert_logo.jpg"):
        candidate = os.path.join(script_dir, filename)
        if os.path.exists(candidate):
            return candidate
    return None


def make_round_logo(size):
    logo_file = resolve_logo_path()
    badge = Image.new("RGBA", (size, size), (12, 12, 12, 255))

    if logo_file:
        try:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((int(size * 0.82), int(size * 0.82)), Image.LANCZOS)
            x = (size - logo.width) // 2
            y = (size - logo.height) // 2
            badge.alpha_composite(logo, (x, y))
        except Exception as e:
            print(f"Logo load failed: {e}")
    else:
        draw = ImageDraw.Draw(badge)
        font = get_font(int(size * 0.34), bold=True)
        text = "LX"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_x = (size - (bbox[2] - bbox[0])) // 2
        text_y = (size - (bbox[3] - bbox[1])) // 2 - 2
        draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

    circle_mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(circle_mask)
    mask_draw.ellipse((0, 0, size - 1, size - 1), fill=255)
    badge.putalpha(circle_mask)

    border = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0))
    border_draw = ImageDraw.Draw(border)
    border_draw.ellipse((0, 0, size + 7, size + 7), fill=(255, 255, 255, 235))
    border.alpha_composite(badge, (4, 4))
    return border


def scaled_alpha(mask, opacity):
    opacity = max(0, min(255, int(opacity)))
    return mask.point(lambda pixel: int(pixel * opacity / 255))


def make_center_watermark(max_width, max_height, opacity, shadow_opacity=center_watermark_shadow_opacity):
    opacity = max(0, min(255, int(opacity)))
    shadow_opacity = max(0, min(255, int(shadow_opacity)))
    logo_file = resolve_logo_path()

    if logo_file:
        try:
            logo = Image.open(logo_file).convert("RGBA")
        except Exception as e:
            print(f"Center watermark logo load failed: {e}")
            logo = None
    else:
        logo = None

    if logo:
        logo.thumbnail((max_width, max_height), Image.LANCZOS)
        mark_mask = logo.convert("L")
        mark_mask = ImageEnhance.Contrast(mark_mask).enhance(2.8)
        mark_mask = mark_mask.point(lambda pixel: 0 if pixel < 70 else min(255, int((pixel - 70) * 1.55)))
        mark_mask = mark_mask.filter(ImageFilter.GaussianBlur(0.45))
    else:
        logo = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
        mark_mask = Image.new("L", (max_width, max_height), 0)
        draw = ImageDraw.Draw(mark_mask)
        font = get_font(int(min(max_width, max_height) * 0.28), bold=True)
        text = "LootsXpert"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_x = (max_width - (bbox[2] - bbox[0])) // 2
        text_y = (max_height - (bbox[3] - bbox[1])) // 2
        draw.text((text_x, text_y), text, fill=255, font=font)

    pad = 18
    watermark = Image.new("RGBA", (logo.width + pad * 2, logo.height + pad * 2), (0, 0, 0, 0))

    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 255))
    shadow.putalpha(scaled_alpha(mark_mask.filter(ImageFilter.GaussianBlur(2.2)), shadow_opacity))
    watermark.alpha_composite(shadow, (pad + 5, pad + 6))

    stamp = Image.new("RGBA", logo.size, (255, 255, 255, 255))
    stamp.putalpha(scaled_alpha(mark_mask, opacity))
    watermark.alpha_composite(stamp, (pad, pad))

    dark_stamp = Image.new("RGBA", logo.size, (0, 0, 0, 255))
    dark_stamp.putalpha(scaled_alpha(mark_mask, int(opacity * 0.35)))
    watermark.alpha_composite(dark_stamp, (pad + 2, pad + 2))

    return watermark


def add_branding_to_image(
        image,
        text=brand_banner_text,
        center_logo_scale=center_watermark_scale,
        center_logo_opacity=center_watermark_opacity,
        center_logo_shadow_opacity=center_watermark_shadow_opacity):
    image = image.convert("RGBA")
    width, height = image.size

    if center_logo_scale > 0 and center_logo_opacity > 0:
        watermark_width = max(1, int(width * center_logo_scale))
        watermark_height = max(1, int(height * center_logo_scale))
        watermark = make_center_watermark(
            watermark_width,
            watermark_height,
            center_logo_opacity,
            center_logo_shadow_opacity
        )
        watermark_x = (width - watermark.width) // 2
        watermark_y = (height - watermark.height) // 2
        image.alpha_composite(watermark, (watermark_x, watermark_y))

    banner_height = max(64, int(height * 0.115))
    banner = Image.new("RGBA", (width, banner_height), (12, 12, 12, 232))
    banner_draw = ImageDraw.Draw(banner)
    banner_draw.rectangle((0, 0, width, 4), fill=(255, 255, 255, 225))

    font = get_font(int(banner_height * 0.46), bold=True)
    bbox = banner_draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_position = ((width - text_width) // 2, (banner_height - text_height) // 2 - 2)
    banner_draw.text(text_position, text, fill=(255, 255, 255, 255), font=font)
    image.alpha_composite(banner, (0, height - banner_height))

    logo_size = max(72, int(min(width, height) * 0.13))
    margin = max(18, int(min(width, height) * 0.035))
    shadow = Image.new("RGBA", (logo_size + 14, logo_size + 14), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.ellipse((7, 7, logo_size + 13, logo_size + 13), fill=(0, 0, 0, 105))
    image.alpha_composite(shadow, (margin - 2, margin - 2))
    image.alpha_composite(make_round_logo(logo_size), (margin, margin))

    return image.convert("RGB")


def findpcode(url):
    try:
        product_code_match = re.search(r"/product/([A-Za-z0-9]{10})", url)
        product_code_match2 = re.search(r'/dp/([A-Za-z0-9]{10})', url)
        product_code = product_code_match.group(1) if product_code_match else product_code_match2.group(1)
        return product_code
    except Exception as e:
        return


def compilehyperlink(message):
    text = message.caption if message.caption else message.text
    inputvalue = text
    hyperlinkurl = []
    entities = message.caption_entities if message.caption else message.entities
    entities = entities or []
    for entity in entities:
        # new_entities.append(entity)
        if entity.url is not None:
            hyperlinkurl.append(entity.url)
    pattern = re.compile(r'Buy Now')

    inputvalue = pattern.sub(lambda x: hyperlinkurl.pop(0), inputvalue).replace('Regular Price', 'MRP')
    if "😱 Deal Time" in inputvalue:
        # Remove the part
        inputvalue = removedup(inputvalue)
        inputvalue = (inputvalue.split("😱 Deal Time")[0]).strip()
    return inputvalue

def make_16_9_with_padding(file_bytes, target_width=1280, target_height=720):
    file_bytes.seek(0)
    img = Image.open(file_bytes).convert("RGB")

    original_width, original_height = img.size

    # Calculate scale while preserving aspect ratio
    scale = min(target_width / original_width, target_height / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    resized_img = img.resize((new_width, new_height), Image.LANCZOS)

    # Create white background
    background = Image.new("RGB", (target_width, target_height), (255, 255, 255))

    # Center image
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2

    background.paste(resized_img, (paste_x, paste_y))
    background = add_branding_to_image(background)

    output = BytesIO()
    background.save(output, format="JPEG", quality=95)
    output.seek(0)

    return output
def should_notify(chat_id: int) -> bool:
    """Return True if this post should notify, False if silent."""
    global post_counter, silent_interval
    if chat_id not in post_counter:
        post_counter[chat_id] = 0
    post_counter[chat_id] += 1
    return post_counter[chat_id] % silent_interval == 0

def should_block_message(text: str) -> bool:
    """
    Block if '@' is followed by ANY letter (a-z / A-Z) without a space.
    Allow if '@' is followed ONLY by digits (price like @141).
    """
    if not text:
        return False

    # find all occurrences of @something
    matches = re.findall(r"@([A-Za-z0-9_]+)", text)

    for m in matches:
        # if it starts with digits ONLY → allowed
        if m.isdigit():
            continue

        # if it contains any alphabet → block
        if re.search(r"[A-Za-z]", m):
            return True

    return False


def strip_html_tags(text):
    return re.sub(r"<[^>]+>", "", text or "").strip()


def clean_ai_caption(text):
    text = (text or "").strip()
    text = text.replace("```", "")
    text = strip_html_tags(text)
    lines = [line.strip(" -\t") for line in text.splitlines() if line.strip(" -\t")]
    return "\n".join(lines[:6]).strip()


def rewrite_deal_text_sync(text):
    if not openai_api_key or not text:
        return text

    urls = extract_link_from_text2(text)
    system_prompt = (
        "Rewrite Telegram shopping deal captions for a child deals channel. "
        "Make it short, clean, original, and easy to read. "
        "Slightly change the caption but it should mean to that specific product."
        "Dont make lengthy or spammy texts"
        "Use 1-2 relevant emojis."
        "Line space needed as per source message. Means make line space betwwn texts and links to beautify the caption"
        "Keep exact prices, coupons, bank offers, product names, and every URL unchanged. "
        "Remove source channel names, forwarded labels, spammy lines. "
        "Return plain text only, no Markdown and no HTML"
    )
    user_prompt = f"Rewrite this deal caption:\n\n{text}"

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {openai_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": openai_model,
                "instructions": system_prompt,
                "input": user_prompt,
                "max_output_tokens": 180,
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        rewritten = clean_ai_caption(data.get("output_text"))

        if not rewritten:
            for item in data.get("output", []):
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        rewritten = clean_ai_caption(content.get("text"))
                        break
                if rewritten:
                    break

        if not rewritten:
            return text

        for url in urls:
            if url not in rewritten:
                print("AI caption skipped because a URL was changed or removed.")
                return text

        return rewritten
    except Exception as e:
        print(f"AI caption rewrite failed: {e}")
        return text


async def rewrite_child_deal_text(text):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, rewrite_deal_text_sync, text)

async def send(id, message,processed):

    text2 = message.caption if message.caption else message.text
    if should_block_message(text2):
        await app.send_message(chat_id=5886397642,text='Just Blocked a Promo')
        return

    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔴 Loot All Deals", url="https://t.me/Loots_Vault/6"),
          InlineKeyboardButton("💬 WhatsApp", url="https://whatsapp.com/channel/0029VanqFQ6KgsNlKMERas3P")]]
    )
    notify = should_notify(id)   # ✅ Added line

    if message.photo:
        try:
            modifiedtxt = compilehyperlink(message).replace('@under_99_loot_deals', '@shopsymeesho')
            modifiedtxt = await rewrite_child_deal_text(modifiedtxt)
            if processed is None:
                file_bytes = await message.download(in_memory=True)
                processed = make_16_9_with_padding(file_bytes)

            if 'tinyurl' in modifiedtxt or 'amazon' in modifiedtxt:
                # print('amzn working')
                urls = extract_link_from_text2(modifiedtxt)
                Newtext = modifiedtxt
                for url in urls:
                    Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
                await app.send_photo(chat_id=id,
                                     # photo=message.photo.file_id,
                                     photo=processed,
                                     caption=f'<b>{Newtext}</b>' + "\n\n<b>👉 <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE & Join All Deals</a> 👈</b>",
                                     reply_markup=Promo,
                                     disable_notification=not notify)
            else:
                await app.send_photo(chat_id=id,
                                     # photo=message.photo.file_id,
                                     photo=processed,
                                     caption=f'<b>{modifiedtxt}</b>' + "\n\n<b>🛍️ 👉 <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE & Join All Deals</a> 👈</b>",
                                     reply_markup=Promo, disable_notification=not notify)


        except Exception as e:
            print(f"❌ Error in send function: {e}")



    elif message.text:
        modifiedtxt = compilehyperlink(message).replace('@under_99_loot_deals', '@shopsymeesho')
        modifiedtxt = await rewrite_child_deal_text(modifiedtxt)

        if 'tinyurl' in modifiedtxt or 'amazon' in modifiedtxt:
            urls = extract_link_from_text2(modifiedtxt)
            Newtext = modifiedtxt

            for url in urls:
                Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
            await app.send_message(chat_id=id,
                                   text=f'<b>{Newtext}</b>',
                                   disable_web_page_preview=True, disable_notification=not notify)
        else:
            await app.send_message(chat_id=id,
                                   text=f'<b>{modifiedtxt}</b>',
                                   disable_web_page_preview=True, disable_notification=not notify)

def extract_price_regex(text: str):
    if not text:
        return None
    # Common INR price patterns: ₹149, Rs. 149, INR 149, 149/-, 149 rs
    patterns = [
        r"(?:₹|Rs\.?\s*|INR\s*)(\d{1,6}(?:\.\d{1,2})?)",
        r"(\d{1,6}(?:\.\d{1,2})?)\s*/-",
        r"(\d{1,6}(?:\.\d{1,2})?)\s*(?:rs|inr)\b",
        r"price\s*[:\-]?\s*(?:₹\s*)?(\d{1,6}(?:\.\d{1,2})?)",
    ]
    candidates = []
    for p in patterns:
        for m in re.findall(p, text, flags=re.IGNORECASE):
            try:
                candidates.append(float(m))
            except:
                continue
    if not candidates:
        return None
    # Return the minimum plausible price found
    return min(candidates)


def extract_price_ai(text: str):
    if not text or client is None:
        return None
    prompt = f"""
    Extract the most likely current price in Indian Rupees from the text.
    - If multiple prices are present (e.g., MRP, deal price), return the LOWEST deal/final price.
    - Return ONLY a number (no currency symbol), like 149 or 149.00.
    - If no price is present, return "None".

    Text:
    {text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract the lowest deal price in INR as a number only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        content = (response.choices[0].message.content or "").strip()
        if content.lower() == "none":
            return None
        # keep only first number if any additional text slipped
        m = re.search(r"\d+(?:\.\d+)?", content)
        if not m:
            return None
        return float(m.group(0))
    except Exception as e:
        print(f"❌ GPT price extraction error: {e}")
        return None


def get_product_price(text: str):
    # Try regex first
    price = extract_price_ai(text)
    if price is not None:
        return price
    # Fallback to AI
    # return extract_price_ai(text)


@bot.route('/')
async def hello():
    return 'Hello, world!'


@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await app.send_message(message.chat.id, "ahaann")

@app.on_message(filters.regex("silent_") & filters.user(5886397642))
async def set_silent_interval(client, message):
    global silent_interval
    try:
        __, arg = message.text.split('_')
        silent_interval = int(arg)
        await message.reply_text(f"✅ Silent interval set: Every {silent_interval} post will notify.")
    except:
        await message.reply_text("❌ Usage: /silent_2")


################forward on off#################################################################
global forward
forward = True


@app.on_message(filters.command('forward') & filters.user(5886397642))
async def forwardtochannel(app, message):
    await message.reply(text='Forward Status', reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("Turn ON", callback_data='forward on')],
         [InlineKeyboardButton("Turn Off", callback_data='forward off')]])
                        )


forward_off = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Turn Off", callback_data='forward off')]])
forward_on = InlineKeyboardMarkup(
    [[InlineKeyboardButton("Turn ON", callback_data='forward on')]])


@app.on_callback_query()
async def callback_query(app, CallbackQuery):
    global forward
    if CallbackQuery.data == 'forward off':
        await CallbackQuery.edit_message_text('Forward to Channel Status turned Off', reply_markup=forward_on)
        forward = False
    elif CallbackQuery.data == 'forward on':
        await CallbackQuery.edit_message_text('Forward to Channel Status turned On', reply_markup=forward_off)
        forward = True

async def send_budget_149(message, final_caption: str):
    if not BUDGET_CHANNEL_ID:
        return

    try:
        extra_html = (
            "\n\n<b>🛍️ 👉 "
            "<a href='https://t.me/addlist/3G8HfhX3WSEwNmI1'>"
            "Click & Join More Deals"
            "</a></b>"
        )

        promo = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🏠 Join Secret Deals",
                        url="https://t.me/+vUHFBOFLHd02MTZl"
                    )
                ]
            ]
        )

        if message.photo:
            await app.send_photo(
                chat_id=BUDGET_CHANNEL_ID,
                photo=message.photo.file_id,
                # caption=f"<b>{final_caption}</b>{extra_html}",
                caption=f"<b>{final_caption}</b>",
                reply_markup=promo
            )

        else:
            await app.send_message(
                chat_id=BUDGET_CHANNEL_ID,
                text=f"<b>{final_caption}</b>",
                disable_web_page_preview=True
            )

        print(f"💸 Budget post sent to {BUDGET_CHANNEL_ID}")

    except FloodWait as e:
        print(f"FloodWait: sleeping {e.value}s")
        await asyncio.sleep(e.value)

    except Exception as e:
        print(f"❌ Error sending to budget channel: {e}")


########################################################################################
last_processed_time = 0
@app.on_message(filters.chat(source_channel_id))
async def forward_message(client, message):
    global last_processed_time
    current_time = asyncio.get_event_loop().time()

    if current_time - last_processed_time < 5:  # 👈 adjust seconds
        print("⚠️ Blocked fast message:", message.id)
        await app.send_message(chat_id=5886397642,text='Blocked fast messages')
        return
    
    last_processed_time = current_time
    if forward == True:
        inputvalue = ''
        processed = None

    # Extract message text/caption first
        if message.caption:
            inputvalue = message.caption
        elif message.text:
            inputvalue = message.text
        price = get_product_price(inputvalue)

        if price is not None and price <= 149:
            print("🔥 Sending to budget channel")
            await send_budget_149(message, inputvalue)
        processed = None

        if message.photo:
            inputvalue = message.caption or ''
            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.url is not None:
                        inputvalue = entity.url
                        break

            file_bytes = await message.download(in_memory=True)
            processed = make_16_9_with_padding(file_bytes)

            try:
                processed.seek(0)
                await app.edit_message_media(chat_id=message.chat.id,message_id=message.id,
                        media=InputMediaPhoto(
                        media=processed,
                        caption=message.caption
                    ),
                    reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(
                        "🏠 Join LootsVault | Save Money 💰",
                        url="https://t.me/addlist/3G8HfhX3WSEwNmI1"
                    )]]
                    )
                )
            except Exception as e:
                print(e)

        elif message.text:
            inputvalue = message.text
            if message.entities:
                for entity in message.entities:
                    if entity.url is not None:
                        inputvalue = entity.url
                        break

        if any(keyword in inputvalue for keyword in shortnerfound):
            # print(extract_link_from_text(inputvalue))
            # inputvalue= unshorten_url(extract_link_from_text(inputvalue))
            unshortened_urls = {}
            urls = extract_link_from_text2(inputvalue)
            for url in urls:
                # if 'extp' in url or 'bitli' in url:
                unshortened_urls[url] = unshorten_url2(url)
                # else:
                # unshortened_urls[url] = await unshorten_url(url)

            for original_url, unshortened_url in unshortened_urls.items():
                inputvalue = inputvalue.replace(original_url, unshortened_url)

        for keywords, chat_id in keyword_to_chat_id.items():
            if any(keyword in inputvalue for keyword in keywords):
                await send(chat_id, message, processed)



@app.on_message(filters.chat(private_channel))
async def forward_message(client, message):
    # print('pp', message.id)

    text = message.caption or message.text or ""
    text = text.replace('- Sent via TeleFeed', '').replace('• Sent via TeleFeed', '')
    if not text:
        return

    text2 = None  # 🔑 IMPORTANT

    try:
        if 'amazon.in' in text:
            text2 = await asyncio.get_event_loop().run_in_executor(
                None, ekconvert, text
            )
            print(f'Found a Shopsy/Amazon deal with ID {message.id}')

        if text2 and 'We could not locate' not in text2:
            text = text2
        else:
            print('aff url not found')

        if message.photo:
            await app.edit_message_caption(
                chat_id=message.chat.id,
                message_id=message.id,
                caption=text
            )
        else:
            await app.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.id,
                text=text,
                disable_web_page_preview=True
            )

    except Exception as e:
        print("Conversion failed:", repr(e))


def ekconvert(text):
    url = "https://ekaro-api.affiliaters.in/api/converter/public"

    # inputtext = input('enter deal: ')
    payload = json.dumps({
        "deal": f"{text}",
        "convert_option": "convert_only"
    })
    headers = {
        'Authorization': f'Bearer {apitoken}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    response_dict = json.loads(response.text)

    # Extract the "data" part from the dictionary
    data_value = response_dict.get('data')

    return (data_value)


def ekconvert(text):
    url = "https://ekaro-api.affiliaters.in/api/converter/public"

    # inputtext = input('enter deal: ')
    payload = json.dumps({
        "deal": f"{text}",
        "convert_option": "convert_only"
    })
    headers = {
        'Authorization': f'Bearer {apitoken}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)
    response_dict = json.loads(response.text)

    # Extract the "data" part from the dictionary
    data_value = response_dict.get('data')

    return(data_value)

CHANNEL_USERNAMES = [
    "@all_amazn_deals",     # flipkart_id
    "@All_fkrt_deals",       # meesho_id
    "@myntr_ajiio_Deals",         # ajiomyntra_i
    "@Dealsunder149",
     "@shopsi_meeso_deals"
  # BUDGET_CHANNEL_ID
    # source channel and private_channel — add usernames if they have one
    # None entries are skipped automatically
]
# ⚠️ IMPORTANT: Replace the dummy usernames above with the real @usernames
# of your channels. Get them from channel Info > Link > Public Link.
# For private channels with no username, set to None.


async def resolve_peers():
    """
    Resolve all channel peers by @username at startup.
    This populates Pyrogram's internal peer storage with real access_hashes,
    so numeric IDs work for the rest of the bot's lifetime.
    """
    failed = []
    for username in CHANNEL_USERNAMES:
        if username is None:
            continue
        try:
            chat = await app.get_chat(username)
            print(f"✅ Peer resolved: {username} → {chat.id}")
        except Exception as e:
            failed.append(username)
            print(f"⚠️ Could not resolve peer {username}: {e}")
    if failed:
        print(f"❌ Failed (wrong username or bot not admin): {failed}")

@bot.before_serving
async def before_serving():
    await app.start()
    await resolve_peers()
    await app.send_message(chat_id= 5886397642, text='Bot starting')


@bot.after_serving
async def after_serving():
    await app.send_message(chat_id= 5886397642, text='Bot Stopping')
    await app.stop()


# if __name__ == '__main__':

# bot.run(port=8000)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run_task(host='0.0.0.0', port=8080))
    loop.run_forever()
