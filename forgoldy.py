import tempfile
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

# from playwright.async_api import async_playwright
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt
# from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a handler for the /start command
bot = Quart(__name__)
# bot.config['PROVIDE_AUTOMATIC_OPTIONS'] = True
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002365489797]  # Replace with the source channel ID
amazon_id = -1002385099278
flipkart_id = -1002347373294
meesho_id = -1002466670728
ajiomyntra_id = -1002410844336
zepto_id= -1003059572977
# cc_id = -1002078634799
# beauty_id = -1002046497963

zepto_keywords=['jiomart','Amazon Fresh','blinkit','zepto','swiggy','bigbasket','Instamart','Flipkart minutes','instamart','Blinkit',
                'Zepto','Swiggy','flipkart minutes','minutes loot']
amazon_keywords = ['amzn', 'amazon', 'tinyurl','amazn']
flipkart_keywords = ['fkrt', 'flipkart', 'boat', 'croma', 'tatacliq', 'fktr', 'Boat', 'Tatacliq', 'noise', 'firebolt']
meesho_keywords = ['meesho', 'shopsy', 'msho', 'wishlink']
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

shortnerfound = ['extp', 'bitli', 'bit.ly', 'bitly', 'bitili', 'biti','bittli']

# tuple(amazon_keywords): amazon_id,
keyword_to_chat_id = {
    tuple(zepto_keywords):zepto_id,
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
silent_interval = 2   # Default: notify every 2nd post
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


def add_banner_to_image(image, text):
    draw = ImageDraw.Draw(image)
    width, height = image.size
    banner_height = int(height * 0.12)  # Banner size (12% of image height)

    # Create a banner overlay
    banner = Image.new("RGB", (width, banner_height), color=(255, 0, 0))  # Red banner
    draw_banner = ImageDraw.Draw(banner)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", size=int(banner_height * 0.97))  # Adjust font size
    except:
        font = ImageFont.load_default()  # Use default if arial.ttf is missing

    # Get text bounding box (new method)
    bbox = draw_banner.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Center text on the banner
    text_position = ((width - text_width) // 2, (banner_height - text_height) // 2)
    draw_banner.text(text_position, text, fill="white", font=font)

    # Append banner to image
    combined_image = Image.new("RGB", (width, height + banner_height))
    combined_image.paste(image, (0, 0))
    combined_image.paste(banner, (0, height))

    return combined_image


def compilehyperlink(message):
    text = message.caption if message.caption else message.text
    inputvalue = text
    hyperlinkurl = []
    entities = message.caption_entities if message.caption else message.entities
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
  
async def send(id, message):
    text2 = message.caption if message.caption else message.text
    if should_block_message(text2):
        # await app.send_message(chat_id=5886397642,text='Just Blocked a Promo')
        return
    # https://t.me/+EUkke-EZOcMxMGE1
    Promo = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔴 Loot All Deals", url="https://t.me/Loots_Vault/6"),
          InlineKeyboardButton("💬 WhatsApp", url="https://whatsapp.com/channel/0029VanqFQ6KgsNlKMERas3P")]]
    )
    notify = should_notify(id)   # ✅ Added line

    if message.photo:
        try:
            modifiedtxt = compilehyperlink(message).replace('@under_99_loot_deals', '@shopsy_meesho_Deals')

            # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            #     await message.download(file_name=temp_file.name)
            #     original_image = Image.open(temp_file.name).convert("RGB")

            # # Debug: Check if image is loaded correctly
            # if original_image is None:
            #     print("❌ Error: Image not loaded properly!")
            #     return

            # # Create a bannered image
            # banner_text = BANNER_MESSAGES.get(id, "🔥 LIMITED DEALS 🔥")  # Default message if ID is not found
            # bannered_image = add_banner_to_image(original_image, banner_text)

            # # Debug: Check if bannered image is created properly
            # if bannered_image is None:
            #     print("❌ Error: add_banner_to_image() returned None!")
            #     return

            # # Save modified image to BytesIO
            # image_bytes = BytesIO()
            # bannered_image.save(image_bytes, format="JPEG")  # ✅ Avoids 'NoneType' error
            # image_bytes.seek(0)

            # Modify caption with "Buy Now" links
            if 'tinyurl' in modifiedtxt or 'amazon' in modifiedtxt:
                # print('amzn working')
                urls = extract_link_from_text2(modifiedtxt)
                Newtext = modifiedtxt
                for url in urls:
                    Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
                await app.send_photo(chat_id=id, photo=message.photo.file_id,
                                     caption=f'<b>{Newtext}</b>' + "\n\n<b>👉 <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE & Join All Deals</a> 👈</b>",
                                     reply_markup=Promo,
                                     disable_notification = not notify )
            else:
                await app.send_photo(chat_id=id, photo=message.photo.file_id,
                                     caption=f'<b>{modifiedtxt}</b>' + "\n\n<b>🛍️ 👉 <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE & Join All Deals</a> 👈</b>",
                                     reply_markup=Promo,disable_notification = not notify)

        except Exception as e:
            print(f"❌ Error in send function: {e}")



    elif message.text:
        modifiedtxt = compilehyperlink(message).replace('@under_99_loot_deals', '@shopsy_meesho_Deals')
        if 'tinyurl' in modifiedtxt or 'amazon' in modifiedtxt:
            urls = extract_link_from_text2(modifiedtxt)
            Newtext = modifiedtxt

            for url in urls:
                Newtext = Newtext.replace(url, f'<b><a href={url}>Buy Now</a></b>')
            await app.send_message(chat_id=id,
                                   text=f'<b>{Newtext}\n\nＬｏｏｔｓＶａｕｌｔ</b>',
                                   disable_web_page_preview=True,disable_notification = not notify)
        else:
            await app.send_message(chat_id=id,
                                   text=f'<b>{modifiedtxt}\n\nＬｏｏｔｓＶａｕｌｔ</b>',
                                   disable_web_page_preview=True,disable_notification = not notify)


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


########################################################################################

@app.on_message(filters.chat(source_channel_id))
async def forward_message(client, message):
    if forward == True:
        inputvalue = ''
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.url is not None:
                    inputvalue = entity.url
            # print(hyerlinkurl)
            if inputvalue == '':
                text = message.caption if message.caption else message.text
                inputvalue = text

        if message.entities:
            for entity in message.entities:
                if entity.url is not None:
                    inputvalue = entity.url
            # print(hyerlinkurl)
            if inputvalue == '':
                text = message.text
                inputvalue = text

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
                await send(chat_id, message)


@bot.before_serving
async def before_serving():
    await app.start()


@bot.after_serving
async def after_serving():
    await app.stop()


# if __name__ == '__main__':

# bot.run(port=8000)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(bot.run_task(host='0.0.0.0', port=8080))
    loop.run_forever()














