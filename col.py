import hashlib
import base58
import ecdsa
import secrets
from Crypto.Hash import RIPEMD160

# آدرس‌های تعریف‌شده در کد
TARGET_ADDRESS = ["19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG"]

RANGE_START = int("0000000000000000000000000000000000000000000000100000000000000000", 16)
RANGE_END = int("00000000000000000000000000000000000000000000001fffffffffffffffff", 16)

def load_addresses_from_file(file_path="addresses.txt"):
    """خواندن آدرس‌های بیت‌کوین از فایل متنی"""
    try:
        with open(file_path, 'r') as file:
            # خواندن خطوط فایل و حذف فضاهای خالی
            addresses = [line.strip() for line in file if line.strip()]
        return addresses
    except FileNotFoundError:
        print(f"خطا: فایل {file_path} یافت نشد.")
        return []
    except Exception as e:
        print(f"خطا در خواندن فایل: {e}")
        return []

def private_key_to_compressed_address(private_key_int):
    private_key_bytes = private_key_int.to_bytes(32, byteorder='big')

    # Generate public key (compressed)
    sk = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
    vk = sk.verifying_key
    x = vk.pubkey.point.x()
    y = vk.pubkey.point.y()
    prefix = b'\x02' if y % 2 == 0 else b'\x03'
    compressed_pubkey = prefix + x.to_bytes(32, byteorder='big')

    # Hash160 (RIPEMD160(SHA256(pubkey)))
    sha256 = hashlib.sha256(compressed_pubkey).digest()
    ripemd160 = RIPEMD160.new()
    ripemd160.update(sha256)
    hashed_pubkey = ripemd160.digest()

    # Add version byte (mainnet) and checksum
    versioned = b'\x00' + hashed_pubkey
    checksum = hashlib.sha256(hashlib.sha256(versioned).digest()).digest()[:4]
    address = base58.b58encode(versioned + checksum).decode()

    return address

def private_key_to_WIF(private_key_int):
    private_key_bytes = private_key_int.to_bytes(32, byteorder='big')
    extended_key = b'\x80' + private_key_bytes + b'\x01'  # For compressed key
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    wif = base58.b58encode(extended_key + checksum).decode()
    return wif

def search_address(order='random', file_path="addresses.txt"):
    checked = 0
    # ترکیب آدرس‌های کد با آدرس‌های فایل
    target_addresses = TARGET_ADDRESS + load_addresses_from_file(file_path)
    if not target_addresses:
        print("هیچ آدرسی برای جستجو وجود ندارد!")
        return

    print(f"تعداد آدرس‌های هدف: {len(target_addresses)}")

    if order == 'sequential':
        current = RANGE_START
        while current <= RANGE_END:
            address = private_key_to_compressed_address(current)
            checked += 1

            if checked % 10000 == 0:
                print(f"🔄 Checked: {checked} | Private Key: {hex(current)} | Address: {address}")

            if address in target_addresses:
                print("\n🎯 MATCH FOUND!")
                print(f"🔑 Private Key (HEX): {hex(current)}")
                print(f"🔐 Private Key (WIF): {private_key_to_WIF(current)}")
                print(f"🏦 Bitcoin Address: {address}")
                print("✅ Search complete. Exiting...")
                return

            current += 1

    else:
        while True:
            key = secrets.randbelow(RANGE_END - RANGE_START) + RANGE_START
            address = private_key_to_compressed_address(key)
            checked += 1

            if checked % 10000 == 0:
                print(f"🔄 Checked: {checked} | Private Key: {hex(key)} | Address: {address}")

            if address in target_addresses:
                print("\n🎯 MATCH FOUND!")
                print(f"🔑 Private Key (HEX): {hex(key)}")
                print(f"🔐 Private Key (WIF): {private_key_to_WIF(key)}")
                print(f"🏦 Bitcoin Address: {address}")
                print("✅ Search complete. Exiting...")
                return

if __name__ == "__main__":
    file_path =  "/content/asdasdas/addresses.txt"
    mode = 'random'
    search_address(order=mode, file_path=file_path)
