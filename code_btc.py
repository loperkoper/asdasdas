import hashlib
import time
from ecdsa import SigningKey, SECP256k1
from eth_keys import keys
from eth_utils import to_checksum_address
import bitcoin
from bitcoin import *
from concurrent.futures import ThreadPoolExecutor

# خواندن فایل wordlist ردیف به ردیف
def read_wordlist_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

# خواندن فایل آدرس‌ها
def read_address_list(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

# تولید کلید خصوصی از یک کلمه با استفاده از SHA-256
def generate_private_key(word):
    return hashlib.sha256(word.encode('utf-8')).hexdigest()

# تولید آدرس بیت‌کوین از کلید خصوصی
def generate_bitcoin_address(private_key_hex):
    private_key_bytes = bytes.fromhex(private_key_hex)
    sk = SigningKey.from_string(private_key_bytes, curve=SECP256k1)
    vk = sk.get_verifying_key()
    public_key = b'\x04' + vk.to_string()  # اضافه کردن 0x04 برای کلید عمومی
    address = pubkey_to_address(public_key)
    return address

# ذخیره کلید خصوصی و آدرس‌ها در صورت تطابق
def save_match_info(word, private_key, address_type, address):
    with open('/content/matches.txt', 'a', encoding='utf-8') as f:
        f.write(f"Word: {word}\n")
        f.write(f"Private Key: {private_key}\n")
        f.write(f"{address_type} Address: {address}\n")
        f.write("-" * 50 + "\n")

# پردازش هر کلمه
def process_word(word, address_list, counter):
    private_key = generate_private_key(word)
    
    # تولید و بررسی آدرس بیت‌کوین
    btc_address = generate_bitcoin_address(private_key)
    if btc_address in address_list:
        save_match_info(word, private_key, "Bitcoin", btc_address)


    # افزایش شمارنده آدرس‌ها
    counter[0] += 1

# فایل wordlist و فایل آدرس‌ها را بخوانید
wordlist_path = '/content/asdasdas/wordlist.txt'  # مسیر فایل لیست کلمات
address_list_path = '/content/Bitcoin_addresses_LATEST.txt'  # مسیر فایل آدرس‌ها
wordlist_lines = read_wordlist_lines(wordlist_path)
address_list = read_address_list(address_list_path)

# شمارنده آدرس‌ها
counter = [0]

# زمان شروع
start_time = time.time()

# استفاده از چند ریسمانی برای پردازش موازی
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(process_word, word, address_list, counter) for word in wordlist_lines]

# صبر کردن تا تمام عملیات‌ها به پایان برسند
for future in futures:
    future.result()

# زمان پایان
end_time = time.time()

# محاسبه و نمایش سرعت تولید آدرس‌ها
total_time = end_time - start_time
speed = counter[0] / total_time if total_time > 0 else 0
print(f"Total addresses generated: {counter[0]}")
print(f"Total time taken: {total_time:.2f} seconds")
print(f"Address generation speed: {speed:.2f} addresses per second") 

#pip install ecdsa eth_keys eth_utils bitcoin
#pip install eth-hash[pycryptodome]
