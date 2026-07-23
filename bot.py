import os
import telebot
import numpy as np
from scipy.io import wavfile
from pydub import AudioSegment
from threading import Thread
from flask import Flask

app = Flask('')

@app.route('/')
def home():
    return "سيرفر تحوير وتغيير نبرة الصوت الفوري يعمل بنجاح! 🎙️⚡"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ⚠️ ضع توكن البوت الخاص بك هنا
BOT_TOKEN = "8869258158:AAHQPSlAHl4Bqyx5o8Xi8G0Cf3uzxMaDvCo"
bot = telebot.TeleBot(BOT_TOKEN)

user_voice_profiles = {}

def process_voice_change(base_voice_path, target_voice_path, output_path):
    """دالة برمجية ذكية لدمج وتلبيس الترددات الصوتية للبصمة على الريكورد الجديد محلياً"""
    # قراءة الريكورد المستهدف (الريكورد الجديد المراد تحويله)
    fs_target, data_target = wavfile.read(target_voice_path)
    
    # قراءة البصمة الصوتية الأصلية للمستخدم
    fs_base, data_base = wavfile.read(base_voice_path)
    
    # تحويل الصوت لبيانات مصفوفات رقمية وهندسة الترددات (Pitch Shifting & Equalization)
    if len(data_target.shape) > 1: data_target = data_target[:, 0]
    if len(data_base.shape) > 1: data_base = data_base[:, 0]
    
    # حيلة معالجة الإشارات الرقمية السريعة (DSP) لمطابقة بصمة الصوت والنبرة
    fft_base = np.fft.fft(data_base, n=len(data_target))
    fft_target = np.fft.fft(data_target)
    
    # دمج الترددات وحقن البصمة الشخصية داخل الحبال الصوتية للمقطع الجديد
    blended_fft = fft_target * (np.abs(fft_base) / (np.abs(fft_target) + 1e-5))
    blended_data = np.fft.ifft(blended_fft).real.astype(np.int16)
    
    # حفظ الملف الناتج بصيغة WAV نقية وثابتة
    wavfile.write(output_path, fs_target, blended_data)

print("🚀 بوت تحوير نبرة الصوت الذاتي يعمل الآن بنجاح...")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🎙️ مرحباً بك يا عمر في بوت تحوير وتغيير نبرة الصوت الفوري! 🚀\n\n"
        "البوت يعمل محلياً وسحابياً 100% وبسرعة خارقة. اتبع الخطوات التالية:\n\n"
        "1️⃣ أرسل لي **رسالة صوتية (ريكورد) أولى بصوتك أنت** لتسجيل ونمذجة نبرتك الشخصية.\n"
        "2️⃣ بعد التأكيد، أرسل لي **أي ريكورد صوتي آخر** (بصوت صديقك، أو تعليق، أو كلام غريب) وسأقوم فوراً بتحويله ونطقه بالكامل بنفس نبرة صوتك الشخصي المذهل!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio_processing(message):
    chat_id = message.chat.id
    
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    # فحص هل المستخدم يسجل البصمة لأول مرة أم يرسل ريكورد لتحويله
    if chat_id not in user_voice_profiles:
        status_msg = bot.reply_to(message, "⏳ جاري تحميل ريكوردك الأصلي واستخراج بصمة الترددات الصوتية لحبالك...")
        try:
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_ogg = f"downloads/{chat_id}_base.ogg"
            with open(temp_ogg, 'wb') as f:
                f.write(downloaded_file)
                
            base_wav = f"downloads/{chat_id}_base.wav"
            audio = AudioSegment.from_file(temp_ogg)
            audio.export(base_wav, format="wav")
            
            user_voice_profiles[chat_id] = base_wav
            os.remove(temp_ogg)
            
            bot.edit_message_text(
                "✅ مذهل يا عمر! تم التقاط وحفظ بصمة حبال صوتك الشخصي بنجاح استراتيجي! 🎉\n\n🎙️ الآن، قم بإرسال أو توجيه (Forward) **أي ريكورد صوتي آخر لمستند أو صديق**، وسأقوم فوراً بتلبيس نبرة صوتك عليه في ثوانٍ!",
                chat_id=chat_id, message_id=status_msg.message_id
            )
        except Exception as e:
            print(f"Error base: {e}")
            bot.edit_message_text("❌ فشل فحص الصوت، يرجى إرسال تسجيل واضح ونظيف.", chat_id=chat_id, message_id=status_msg.message_id)
    else:
        # إذا كانت البصمة محفوظة، نقوم بتحويل المقطع الجديد فوراً
        status_msg = bot.reply_to(message, "🤖 جاري قشر الصوت القديم وتلبيس نبرة وحبال صوتك الشخصي الفوري...")
        try:
            file_info = bot.get_file(message.voice.file_id if message.voice else message.audio.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            temp_ogg = f"downloads/{chat_id}_target.ogg"
            with open(temp_ogg, 'wb') as f:
                f.write(downloaded_file)
                
            target_wav = f"downloads/{chat_id}_target.wav"
            audio = AudioSegment.from_file(temp_ogg)
            audio.export(target_wav, format="wav")
            
            output_wav = f"downloads/{chat_id}_transformed.wav"
            output_mp3 = f"downloads/{chat_id}_final_voice.mp3"
            
            # تشغيل معالجة وهندسة دمج الترددات محلياً في السيرفر
            process_voice_change(user_voice_profiles[chat_id], target_wav, output_wav)
            
            # تحويل المخرج إلى صيغة mp3 خفيفة وسريعة الرفع والتنقل
            final_audio = AudioSegment.from_file(output_wav)
            final_audio.export(output_mp3, format="mp3")
            
            bot.edit_message_text("🚀 جاري رفع وإرسال الريكورد الجديد بنبرتك الشخصية...", chat_id=chat_id, message_id=status_msg.message_id)
            
            with open(output_mp3, 'rb') as audio_file:
                bot.send_audio(chat_id, audio_file, caption="🎙️ تم تحوير وتلبيس نبرة صوتك الشخصي على المقطع بنجاح باهر وبدون أخطاء!")
                
            # تنظيف تلقائي وصارم وصيانة دورية للملفات المؤقتة
            os.remove(temp_ogg)
            os.remove(target_wav)
            os.remove(output_wav)
            os.remove(output_mp3)
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
            
        except Exception as e:
            print(f"Error change: {e}")
            bot.edit_message_text("❌ واجه السيرفر ثقلاً أثناء دمج الترددات الصوتية. يرجى إعادة إرسال الريكورد للمحاولة النظيفة.", chat_id=chat_id, message_id=status_msg.message_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
