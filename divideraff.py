from io import BytesIO

import requests
from pyrogram import Client, filters, enums
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import asyncio
from quart import Quart
from unshortenit import UnshortenIt
api_id= '20108351'
api_hash= '37cd07faf01b76eea22f270251764859'
bot_token = '7945098659:AAGt0DMQwf9BMtl67ysTFz3QskA0EvD4cls'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a handler for the /start command
bot = Quart(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

source_channel_id = [-1002365489797]  # Replace with the source channel ID
amazon_id = -1002385099278
flipkart_id = -1002347373294
meesho_id = -1002466670728
ajiomyntra_id = -1002410844336


amazon_keywords = ['amzn', 'amazon', 'tinyurl']
flipkart_keywords = ['fkrt', 'flipkart', 'boat', 'croma', 'tatacliq', 'fktr', 'Boat', 'Tatacliq']
ajio_keywords = ['ajiio', 'myntr', 'xyxx','mamaearth', 'bombayshavingcompany', 'beardo', 'Beardo', 'Tresemme', 'themancompany', 'wow', 'nykaa',
                   'mCaffeine', 'Bombay Shaving Company', 'BSC', 'TMC', 'foxtale',
                   'fitspire', 'PUER']
meesho_keywords = ['meesho', 'shopsy', 'msho', 'wishlink']
beauty_keywords = []
# cc_keywords=['axis','hdfc','icici','sbm','sbi','credit','idfc','aubank','hsbc','Axis','Hdfc','Icici','Sbm','Sbi','Credit','Idfc','Aubank','Hsbc',
#             'AXIS','HDFC','ICICI','SBM','SBI','CREDIT','IDFC','AUBANK','HSBC']
cc_keywords = ['Apply Now', 'Lifetime Free', 'Apply for', ' Lifetime free', 'Benifits', 'Apply here', 'Lifetime FREE',
               'ELIGIBILITY', 'Myzone', 'Rupay', 'rupay', 'Complimentary', 'Apply from here', 'annual fee',
               'Annual fee', 'joining fee']

shortnerfound = ['extp', 'bitli', 'bit.ly', 'bitly', 'bitili']

# tuple(amazon_keywords): amazon_id,
keyword_to_chat_id = {
    tuple(amazon_keywords): amazon_id,
    tuple(flipkart_keywords): flipkart_id,
    tuple(meesho_keywords): meesho_id,
    tuple(ajio_keywords): ajiomyntra_id,
}


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


def unshorten_url(short_url):
    unshortener = UnshortenIt()
    shorturi = unshortener.unshorten(short_url)
    # print(shorturi)
    return shorturi


async def send(id, message):
    Promo = InlineKeyboardMarkup(
        [
         [InlineKeyboardButton("Main Channel 🛒", url="https://t.me/deals_by_divya"),
          InlineKeyboardButton("WhatsApp 💬", url="https://whatsapp.com/channel/0029VanqFQ6KgsNlKMERas3P")],
         [InlineKeyboardButton("Loot All Deals 🏠", url="https://t.me/divyadeals2/4")]
         ])

    if message.photo:
        # with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        #     await message.download(file_name=temp_file.name)
        #     with open(temp_file.name, 'rb') as f:
        #         photo_bytes = BytesIO(f.read())
        if 'tinyurl' in message.caption or 'amazon' in message.caption:
            urls = extract_link_from_text2(message.caption)
            Newtext = message.caption

            for url in urls:
                Newtext = Newtext.replace(url, f'<b><a href={unshorten_url(url)}>Buy Now</a></b>')
            await app.send_photo(chat_id=id, photo=message.photo.file_id, caption=f'<b>{Newtext}</b>'+"\n\n<b>More Deals! 👉 : <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE to Join</a></b>",
                                 reply_markup=Promo)
        elif 'wishlink' in message.caption:

            text = message.caption
            Newtext = tinycovert(text)
            await app.send_photo(chat_id=id, photo=message.photo.file_id, caption=f'<b>{Newtext}</b>'+"\n\n<b>More Deals! 👉 : <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE to Join</a></b>",
                                 reply_markup=Promo)
        else:
            await app.send_photo(chat_id=id, photo=message.photo.file_id, caption=f'<b>{message.caption}</b>'+"\n\n<b>More Deals! 👉 : <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE to Join</a></b>",
                                 reply_markup=Promo)




    elif message.text:
        if 'tinyurl' in message.text or 'amazon' in message.text:
            urls = extract_link_from_text2(message.text)
            Newtext = message.text

            for url in urls:
                Newtext = Newtext.replace(url, f'<b><a href={unshorten_url(url)}>Buy Now</a></b>')
            await app.send_message(chat_id=id, text=f'<b>{Newtext}</b>'+"\n\n<b>More Deals! 👉 : <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE to Join</a></b>", disable_web_page_preview=True)
        elif 'wishlink' in message.text:
            text = message.text
            Newtext = tinycovert(text)
            await app.send_message(chat_id=id, text=f"<b>{Newtext}</b>"+"\n\n<b>More Deals! 👉 : <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE to Join</a></b>", disable_web_page_preview=True)
        else:
            await app.send_message(chat_id=id, text=f"<b>{message.text}</b>"+"\n\n<b>More Deals! 👉 : <a href ='https://t.me/addlist/3G8HfhX3WSEwNmI1'>Click HERE to Join</a></b>", disable_web_page_preview=True)


@bot.route('/')
async def hello():
    return 'Hello, world!'


@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await app.send_message(message.chat.id, "ahaann")


@app.on_message(filters.chat(source_channel_id))
async def forward_message(client, message):
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
            unshortened_urls[url] = unshorten_url(url)
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
