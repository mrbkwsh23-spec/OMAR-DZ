import os
import telebot
from gradio_client import Client, handle_file
from pydub import AudioSegment
from threading import Thread
from flask import Flask

# سيرفر الويب الوهمي لمنع أخطاء الـ Ports في Render
app = Flask('')

@app.route('/')
def home():
    return "سيرفر استنساخ ونطق الصوت المستقر يعمل مجاناً 100%! 🎙️🔥"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ⚠️ ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8869258158:AAHQPSlAHl4Bqyx5o8Xi8G0Cf3uzxMaDvCo"
bot = telebot.TeleBot(BOT_TOKEN)

user_voices = {}

print("🚀 بوت استنساخ الصوت السحابي المطور يعمل الآن بنجاح...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎙️ مرحباً بك يا عمر في بوت استنساخ صوتك الشخصي المطور! 🚀\n\n"
        "1️⃣ سجل **رسالة صوتية (ريكورد) بصوتك** الطبيعي مدتها 10 ثوانٍ وأرسلها لي.\n"
        "2️⃣ بعد تأكيد الحفظ، **أرسل أي نص مكتوب بالعربية** وسأنطقه فوراً بنفس نبرة صوتك الحقيقي!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['voice', 'audio'])
def handle_voice_cloning(message):
    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ جاري تحميل الريكورد وتفكيك النبرة الصوتية سحابياً...")

    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    try:
        file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        temp_ogg = f"downloads/{chat_id}_temp.ogg"
        with open(temp_ogg, 'wb') as f:
            f.write(downloaded_file)
            
        clean_wav = f"downloads/{chat_id}_prompt.wav"
        audio = AudioSegment.from_file(temp_ogg)
        audio.export(clean_wav, format="wav")
        
        user_voices[chat_id] = clean_wav
        os.remove(temp_ogg)
        
        bot.edit_message_text(
            "✅ مذهل يا عمر! تم حفظ بصمة صوتك الشخصي بنجاح! 🎉\n\n✍️ الآن اكتب لي أي نص باللغة العربية، وسأقوم بتقليد صوتك ونطقه فوراً!",
            chat_id=chat_id, message_id=status_msg.message_id
        )
        
    except Exception as e:
        print(f"Error saving voice: {e}")
        bot.edit_message_text("❌ فشل تحليل نبرة الصوت. تأكد من تسجيل ريكورد واضح ومدته تزيد عن 5 ثوانٍ.", chat_id=chat_id, message_id=status_msg.message_id)

@bot.message_handler(func=lambda message: True)
def generate_cloned_voice(message):
    chat_id = message.chat.id
    text_to_speak = message.text

    if chat_id not in user_voices or not os.path.exists(user_voices[chat_id]):
        bot.reply_to(message, "⚠️ يرجى تسجيل وإرسال بصمة صوتك (ريكورد) أولاً قبل كتابة النص.")
        return

    status_msg = bot.reply_to(message, "🤖 جاري الاستنساخ الفوري للأحبال الصوتية وتوليد المقطع...")

    try:
        sample_voice_path = user_voices[chat_id]

        # الاتصال السحابي الثابت والمستقر بنظام XTTS-v2 دون مشاكل الهاتف
                # 🟢 تم تبديل السيرفر إلى مساحة سحابية فائقة السرعة وأقل ازدحاماً لضمان الاستجابة الفورية
        client = Client("prodia/XTTS-v2-Fast")

        
        result = client.predict(
            text=text_to_speak,
            language="ar",
            speaker_wav=handle_file(sample_voice_path),
            api_name="/predict"
        )

        output_wav = result

        if os.path.exists(output_wav):
            bot.edit_message_text("🚀 جاري رفع وإرسال مقطع صوتك المستنسخ فائق الجودة...", chat_id=chat_id, message_id=status_msg.message_id)
            
            with open(output_wav, 'rb') as audio_file:
                bot.send_audio(chat_id, audio_file, caption="🎙️ تم استنساخ صوتك الشخصي ونطق كلامك المكتوب بنجاح وبدون قيود!")
                
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        else:
            raise Exception("الملف الناتج غير موجود")

    except Exception as e:
        print(f"Error cloning voice: {e}")
        bot.edit_message_text("❌ حدث ضغط مؤقت في خوادم المعالجة السحابية الحرة، يرجى إعادة إرسال النص الآن لإعادة المحاولة المباشرة والسريعة.", chat_id=chat_id, message_id=status_msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
