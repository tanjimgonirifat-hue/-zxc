import telebot
import pyotp
import requests
import random
import time
import os
import threading
from flask import Flask
from faker import Faker
from concurrent.futures import ThreadPoolExecutor

# --- ⚙️ কনফিগারেশন (Configuration) ---
TOKEN = '8783194900:AAH__MsqIgqwKn_-Pzg2NdxQsIJ1OjvAVY8' 
# আপনার দেওয়া নতুন URL এখানে আপডেট করা হয়েছে
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbw9jzrlG_rhPYm-jW6KgYwcRu05hREKgbNCmHoH6wCgvpnNMnIe_SRMPvVGSCpb41vRtA/exec"
ADMIN_ID = 8061525743 
ADMIN_PASSWORD = "TanJImGonIRifAT2010FD"
BOT_NAME = "𝐓𝐚𝐧𝐣𝐢𝐦 𝐀𝐮𝐭𝐨𝐦𝐚𝐭𝐢𝐨𝐧"

# হাই-স্পিড পারফরম্যান্সের জন্য থ্রেড কনফিগারেশন
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=50)
app = Flask(__name__)
fake = Faker()
executor = ThreadPoolExecutor(max_workers=30)

user_tasks = {}

@app.route('/')
def home():
    return f"🚀 {BOT_NAME} is Live and Fast!"

# গুগল শিটে ডাটা পাঠানোর ফাস্ট ফাংশন
def send_to_sheet(row):
    try:
        requests.post(WEB_APP_URL, json={"row": row}, headers={"Content-Type": "application/json"}, timeout=15)
    except Exception as e:
        print(f"Sheet Error: {e}")

# --- 🎨 মেইন মেনু কিবোর্ড (নিচের সেকশনে সাজানো) ---
def main_menu(user_id):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    markup.row(telebot.types.KeyboardButton('🚀 𝐒𝐭𝐚𝐫𝐭 𝐖𝐨𝐫𝐤'))
    markup.row(
        telebot.types.KeyboardButton('👤 𝐌𝐲 𝐏𝐫𝐨𝐟𝐢𝐥𝐞'), 
        telebot.types.KeyboardButton('💸 𝐖𝐢𝐭𝐡𝐝𝐫𝐚𝐰'), 
        telebot.types.KeyboardButton('👥 𝐌𝐲 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬')
    )
    markup.row(telebot.types.KeyboardButton('🏆 𝐓𝐨𝐩 𝐖𝐨𝐫𝐤𝐞𝐫𝐬'), telebot.types.KeyboardButton('📞 𝐒𝐮𝐩𝐩𝐨𝐫𝐭'))
    markup.row(telebot.types.KeyboardButton('🌍 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞'))
    
    if user_id == ADMIN_ID:
        markup.row(telebot.types.KeyboardButton('🔐 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥'))
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(
        message.chat.id, 
        f"🌟 **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 {BOT_NAME}** 🌟\n━━━━━━━━━━━━━━━━━━\n"
        "আপনার নতুন সিস্টেম এখন পুরোপুরি প্রস্তুত। কাজ শুরু করতে নিচের মেনু ব্যবহার করুন।", 
        reply_markup=main_menu(message.from_user.id), 
        parse_mode="Markdown"
    )

# --- 🔐 অ্যাডমিন প্যানেল লগইন ---
@bot.message_handler(func=lambda message: message.text == "🔐 𝐀𝐝𝐦𝐢𝐧 𝐏𝐚𝐧𝐞𝐥")
def admin_login(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "🔑 **অ্যাডমিন পাসওয়ার্ড দিন:**")
    bot.register_next_step_handler(msg, verify_admin)

def verify_admin(message):
    if message.text == ADMIN_PASSWORD:
        bot.send_message(message.chat.id, "✅ **লগইন সফল!** অ্যাডমিন ড্যাশবোর্ড সক্রিয়।")
    else:
        bot.send_message(message.chat.id, "❌ ভুল পাসওয়ার্ড!")

# --- 🚀 ফাস্ট টাস্ক লজিক ---
@bot.message_handler(func=lambda message: message.text == "🚀 𝐒𝐭𝐚𝐫𝐭 𝐖𝐨𝐫𝐤")
def pick_task(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("📱 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 + 𝟐𝐅𝐀 ⇛ $𝟎.𝟎𝟏𝟕𝟎", callback_data="task_inst"))
    bot.send_message(message.chat.id, "✨ **𝐒𝐞𝐥𝐞𝐜𝐭 𝐘𝐨𝐮𝐫 𝐀𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐓𝐚𝐬𝐤:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "task_inst")
def start_inst(call):
    chat_id = call.message.chat.id
    f_name = f"{fake.first_name()} {fake.last_name()}"
    login = f"{fake.user_name()}{random.randint(10, 99)}"
    pwd = fake.password(length=10)
    
    user_tasks[chat_id] = {"name": f_name, "login": login, "pass": pwd, "start_time": time.time()}
    
    bot.send_message(
        chat_id, 
        f"📝 **𝐍𝐞𝐰 𝐓𝐚𝐬𝐤 𝐀𝐬𝐬𝐢𝐠𝐧𝐞𝐝**\n━━━━━━━━━━━━━\n"
        f"👤 **Name:** `{f_name}`\n📧 **Login:** `{login}`\n🔑 **Pass:** `{pwd}`\n"
        f"━━━━━━━━━━━━━\n⏳ ৪ মিনিটের মধ্যে **2FA Key** দিন।", 
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(call.message, handle_otp)

def handle_otp(message):
    chat_id = message.chat.id
    if not message.text or message.text.startswith('/'): return
    
    if chat_id in user_tasks and (time.time() - user_tasks[chat_id]['start_time'] > 240):
        bot.send_message(chat_id, "⏰ সময় শেষ! টাস্ক বাতিল।")
        user_tasks.pop(chat_id, None)
        return

    try:
        key = message.text.replace(" ", "")
        totp = pyotp.TOTP(key)
        otp = totp.now()
        user_tasks[chat_id]['2fa_key'] = key
        
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("📤 𝐒𝐮𝐛𝐦𝐢𝐭 𝐑𝐞𝐩𝐨𝐫𝐭", callback_data="final_submit"))
        bot.send_message(chat_id, f"🔢 **𝐘𝐨𝐮𝐫 𝐎𝐓𝐏 𝐢𝐬:** `{otp}`\n\n✅ চেক করে রিপোর্ট জমা দিন।", reply_markup=markup, parse_mode="Markdown")
    except:
        bot.send_message(chat_id, "❌ ভুল কী! আবার সঠিক কী দিন।")
        bot.register_next_step_handler(message, handle_otp)

@bot.callback_query_handler(func=lambda call: call.data == "final_submit")
def final_submission(call):
    chat_id = call.message.chat.id
    data = user_tasks.get(chat_id)
    if data:
        row = [time.ctime(), str(chat_id), data['name'], data['login'], data['pass'], data.get('2fa_key', 'N/A'), "Pending"]
        # ব্যাকগ্রাউন্ডে শিটে ডাটা পাঠানো হচ্ছে
        executor.submit(send_to_sheet, row)
        bot.edit_message_text("✅ **সফলভাবে জমা হয়েছে!** শিটে ডাটা সেভ হচ্ছে।", chat_id, call.message.message_id)
        user_tasks.pop(chat_id, None)

# --- 🏆 টপ ওয়ার্কার্স ও অন্যান্য ---
@bot.message_handler(func=lambda message: True)
def handle_menu(message):
    chat_id = message.chat.id
    if message.text == "🏆 𝐓𝐨𝐩 𝐖𝐨𝐫𝐤𝐞𝐫𝐬":
        bot.send_message(chat_id, "🏆 **Top submitters List:**\n1. User#82... : 150 IDs\n2. User#91... : 120 IDs")
    elif message.text == "📞 𝐒𝐮𝐩𝐩𝐨𝐫𝐭":
        bot.send_message(chat_id, "📞 **Admin Support:** @Tanjim_Admin")
    elif message.text == "👤 𝐌𝐲 𝐏𝐫𝐨𝐟𝐢𝐥𝐞":
        bot.send_message(chat_id, f"👤 **Profile:**\n🆔: `{chat_id}`\n💰: $0.0000\n📈: Active")
    elif message.text == "💸 𝐖𝐢𝐭𝐡𝐝𝐫𝐚𝐰":
        bot.send_message(chat_id, "💸 ব্যালেন্স পর্যাপ্ত হলে উইথড্র অপশন কাজ করবে।")

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

if __name__ == '__main__':
    threading.Thread(target=run_web).start()
    bot.infinity_polling()
