import telebot
import requests
import time
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

TOKEN = '6716141167:AAH6ZFzddjpneCELzv7Fty8ogsaxLRZhP5c'
bot = telebot.TeleBot(TOKEN)

user_descriptions_count = {}
regenerate_count = {}
quality_settings = {}
version_settings = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    name = message.from_user.first_name
    welcome_text = (
        f"مرحبا بك {name} 👋🏻 \n\n انا روبوت من صنع وتطوير شركة NotCyberSec السيبرانية تم انشائي بأستخدام تقنية ASD-4500 💻 \n\n يمكنك إرسال الوصف الذي تريده اقبل حقوق NSFW ولدي قدرة علي انشاء ومعالجة الصور الغير أخلاقية بدون قيود يفضل أن يكون وصفك باللغة الإنجليزية وسأقوم بتوليد صورة مطابقة لوصفك عبر الذكاء الاصطناعي 🧬 \n\n بحد أقصي لديك 100 صورة يوميا، ويمكنك الإشتراك في خطة VIP لتحصل علي عدد لا نهائي من الصور 🌟"
    )
    
    markup = telebot.types.InlineKeyboardMarkup()
    owner_button = telebot.types.InlineKeyboardButton("المدير ⚜", url="https://t.me/RRR7ZZZ")
    vip_button = telebot.types.InlineKeyboardButton("ترقية إلي ASD-Plus 👑", callback_data="vip_unlock")
    version_button = telebot.types.InlineKeyboardButton("إصدتر ASD ⚙", callback_data="version")
    markup.add(owner_button, vip_button)
    markup.add(version_button)

    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

def generate_image(message, user_description):
    if user_description in user_descriptions_count:
        user_descriptions_count[user_description] += 1
    else:
        user_descriptions_count[user_description] = 1
        regenerate_count[user_description] = 0
        quality_settings[user_description] = ""
        version_settings[message.chat.id] = ""

    dots = '.' * user_descriptions_count[user_description]
    hyphens = '-' * regenerate_count[user_description]
    quality = quality_settings[user_description]
    version = version_settings[message.chat.id]
    modified_description = user_description + dots + hyphens + quality + version

    formatted_description = modified_description.replace(' ', '%20')
    image_url = f"https://image.pollinations.ai/prompt/{formatted_description}"

    countdown_message = bot.send_message(
        message.chat.id, f'ممتاز 👌🏻 \n\n لقد طلبت {user_description}، سيتم تحديد جودة الصورة والأبعاد الخ الخ بناء علي وصفك او علي اصدار ASD الذي استخدمته لتوليد الصور ☂ \n\n الوقت المقدر لأنشاء الصورة {15}s ⏳'
    )

    for i in range(14, 0, -1):
        time.sleep(1)
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=countdown_message.message_id,
            text=f'ممتاز 👌🏻 \n\n لقد طلبت {user_description}، سيتم تحديد جودة الصورة والأبعاد الخ الخ بناء علي وصفك او علي اصدار ASD الذي استخدمته لتوليد الصور ☂ \n\n الوقت المقدر لأنشاء الصورة {i}s ⏳'
        )

    time.sleep(1)

    response = session.get(image_url)

    if response.status_code == 200:
        with open('image.jpg', 'wb') as file:
            file.write(response.content)
        
        markup = telebot.types.InlineKeyboardMarkup()
        like_button = telebot.types.InlineKeyboardButton("👍🏻", callback_data="like")
        dislike_button = telebot.types.InlineKeyboardButton("👎🏻", callback_data="dislike")
        regenerate_button = telebot.types.InlineKeyboardButton("ReGenerate 🔄", callback_data=f"regenerate:{user_description}")
        quality_button = telebot.types.InlineKeyboardButton("Quality ✨️", callback_data=f"quality:{user_description}")
        markup.row(like_button, dislike_button)
        markup.row(regenerate_button, quality_button)

        bot.send_photo(message.chat.id, open('image.jpg', 'rb'), reply_markup=markup)
        
        os.remove('image.jpg')
    else:
        bot.reply_to(message, 'حدث خطأ في تحميل الصورة. حاول مجدداً بوصف آخر.')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_description = message.text
    generate_image(message, user_description)

@bot.callback_query_handler(func=lambda call: call.data.startswith("regenerate:") or call.data.startswith("quality:") or call.data.startswith("quality_setting:") or call.data.startswith("version_setting:") or call.data in ["like", "dislike", "vip_unlock", "version", "back_to_main"])
def callback_query(call):
    if call.data == "like":
        bot.edit_message_caption(
            caption="لقد اعجبتك تلك الصورة 👍🏻",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    elif call.data == "dislike":
        bot.edit_message_caption(
            caption="لم تعجبك هذه الصورة 👎🏻",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    elif call.data.startswith("regenerate:"):
        user_description = call.data.split(":", 1)[1]
        regenerate_count[user_description] += 1
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        generate_image(call.message, user_description)
    elif call.data.startswith("quality:"):
        user_description = call.data.split(":", 1)[1]
        markup = telebot.types.InlineKeyboardMarkup()
        quality_options = [
            "426x240 SD", "640x480 SD", "1280x720 HD", 
            "1920x1080 HD", "2560x1440 QHD", "3840x2160 4K", "7680x4320 8K"
        ]
        for option in quality_options:
            button = telebot.types.InlineKeyboardButton(option, callback_data=f"quality_setting:{user_description}:{option}")
            markup.add(button)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif call.data.startswith("quality_setting:"):
        _, user_description, quality = call.data.split(":", 3)
        quality_settings[user_description] = f" {quality}"
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        generate_image(call.message, user_description)
    elif call.data == "version":
        markup = telebot.types.InlineKeyboardMarkup()
        version_options = [
            telebot.types.InlineKeyboardButton("ASD-3 Low", callback_data="version_setting:Low quality, unrealistic photo"),
            telebot.types.InlineKeyboardButton("ASD-4 Medium", callback_data="version_setting:Low quality medium realistic photo"),
            telebot.types.InlineKeyboardButton("ASD-5 High", callback_data="version_setting:God quality realistic photo"),
            telebot.types.InlineKeyboardButton("ASD-6 V.High", callback_data="version_setting:Very high quality, hyper realistic, 4K")
        ]
        markup.add(version_options[0], version_options[1])
        markup.add(version_options[2], version_options[3])
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
    elif call.data.startswith("version_setting:"):
        version_setting = call.data.split(":", 1)[1]
        version_settings[call.message.chat.id] = f" {version_setting}"
        name = call.from_user.first_name
        welcome_text = (
            f"مرحبا بك {name} 👋🏻 \n\n انا روبوت من صنع وتطوير شركة NotCyberSec السيبرانية تم انشائي بأستخدام تقنية ASD-4500 💻 \n\n يمكنك إرسال الوصف الذي تريده اقبل حقوق NSFW ولدي قدرة علي انشاء ومعالجة الصور الغير أخلاقية بدون قيود يفضل أن يكون وصفك باللغة الإنجليزية وسأقوم بتوليد صورة مطابقة لوصفك عبر الذكاء الاصطناعي 🧬 \n\n بحد أقصي لديك 100 صورة يوميا، ويمكنك الإشتراك في خطة VIP لتحصل علي عدد لا نهائي من الصور 🌟"
        )
        
        markup = telebot.types.InlineKeyboardMarkup()
        owner_button = telebot.types.InlineKeyboardButton("المدير ⚜", url="https://t.me/RRR7ZZZ")
        vip_button = telebot.types.InlineKeyboardButton("ترقية إلي ASD-Plus 👑", callback_data="vip_unlock")
        version_button = telebot.types.InlineKeyboardButton("إصدار ASD ⚙️", callback_data="version")
        markup.add(owner_button, vip_button)
        markup.add(version_button)

        bot.edit_message_text(
            text=welcome_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    elif call.data == "vip_unlock":
        markup = telebot.types.InlineKeyboardMarkup()
        back_button = telebot.types.InlineKeyboardButton("العودة للرئيسية", callback_data="back_to_main")
        markup.add(back_button)
        bot.edit_message_text(
            text="لقد قام مدير هاذا البوت بتخصيص الأشتراك المميز فقط في الاصدار الكامل من ASD وليس إصدار ASD-Beta ⛔️\n\nانت تستعمل نسخة ASD-Beta لذا انت من المشتركين في ASD-Plus بالفعل 👑",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    elif call.data == "back_to_main":
        name = call.from_user.first_name
        welcome_text = (
            f"مرحبا بك {name} 👋🏻 \n\n انا روبوت من صنع وتطوير شركة NotCyberSec السيبرانية تم انشائي بأستخدام تقنية ASD-4500 💻 \n\n يمكنك إرسال الوصف الذي تريده اقبل حقوق NSFW ولدي قدرة علي انشاء ومعالجة الصور الغير أخلاقية بدون قيود يفضل أن يكون وصفك باللغة الإنجليزية وسأقوم بتوليد صورة مطابقة لوصفك عبر الذكاء الاصطناعي 🧬 \n\n بحد أقصي لديك 100 صورة يوميا، ويمكنك الإشتراك في خطة VIP لتحصل علي عدد لا نهائي من الصور 🌟"
        )
        
        markup = telebot.types.InlineKeyboardMarkup()
        owner_button = telebot.types.InlineKeyboardButton("المدير ⚜", url="https://t.me/RRR7ZZZ")
        vip_button = telebot.types.InlineKeyboardButton("ترقية إلي ASD-Plus 👑", callback_data="vip_unlock")
        version_button = telebot.types.InlineKeyboardButton("إصدار ASD ⚙️", callback_data="version")
        markup.add(owner_button, vip_button)
        markup.add(version_button)

        bot.edit_message_text(
            text=welcome_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )

bot.polling()
  
