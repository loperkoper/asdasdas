import os, random, codecs, time, threading, multiprocessing
from bit.format import bytes_to_wif
from bit import Key
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Worker(threading.Thread):
  def __init__(self, target_file, target_set):
    super().__init__()
    self.target_file = target_file
    self.target_set = target_set
    self.found = []

  def run(self):
    while True:
      Private_Key = _HexGen(64)
      WifCompressed, WifUncompressed = _HexToWif(Hex=Private_Key)
      CompressAddr, UnCompressAddr = _WifToAddr(WifCompressed, WifUncompressed)
      if CompressAddr in self.target_set or UnCompressAddr in self.target_set:
        self.found.append((CompressAddr, UnCompressAddr, Private_Key, WifCompressed, WifUncompressed))

  def get_found(self):
    return self.found

def MainCheck(Target):
  global worker, z, wf

  z = 0
  wf = 0
  lg = 0

  while True:
    z += 1

    found = worker.get_found()

    for f in found:
      wf += 1

      # Write found addresses to a file in a single write operation
      with codecs.open('content/asdasdas/found.txt', 'ab') as f:
        f.writelines(['Compressed Address: {}\n'.format(f[0]),
                      'UnCompressed Address: {}\n'.format(f[1]),
                      'Private Key: {}\n'.format(f[2]),
                      'WIF (Compressed): {}\n'.format(f[3]),
                      'WIF (UnCompressed): {}\n'.format(f[4])])

      def send_email(sender, receiver, subject, body):
                """
                ارسال ایمیل

                Args:
                    sender: آدرس ایمیل فرستنده
                    receiver: آدرس ایمیل گیرنده
                    subject: موضوع ایمیل
                    body: متن ایمیل

                Returns:
                    True اگر ایمیل با موفقیت ارسال شد، در غیر این صورت False
                """

                # اتصال به سرور SMTP
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()

                # لاگین به سرور با نام کاربری و رمز عبور
                sender = "pouriya.guitar@gmail.com"
                server.login(sender, "xecy aomq ddms tmid")

                # ایجاد پیام ایمیل
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = receiver
                msg["Subject"] = subject
                msg.attach(MIMEText(body))

                # ارسال پیام ایمیل
                try:
                    server.sendmail(sender, receiver, msg.as_string())
                    return True
                except Exception as e:
                    print(e)
                    return False

            # تنظیم اطلاعات ایمیل
      sender = "pouriya.guitar@gmail.com"
      receiver = "tatalbet666@gmail.com"
      subject = "هش"
      body = """
    Compressed Address: {}
    UnCompressed Address: {}
    Private Key: {}
    WIF (Compressed): {}
    WIF (UnCompressed): {}
    """.format(f[0], f[1], f[2], f[3], f[4])

            # ارسال ایمیل
      while True:
                if send_email(sender, receiver, subject, body):
                    break
                time.sleep(10)






    if z % 1000000 == 0:
      lg += 1000000
      print('Generated: {} (SHA-256 - HEX) ...'.format(lg))

def _HexGen(size):
  return ''.join(random.choices('0123456789abcdef', k=size))

def _HexToWif(Hex):
  byteHex = bytes.fromhex(Hex)
  return bytes_to_wif(byteHex, compressed=True), bytes_to_wif(byteHex, compressed=False)

def _WifToAddr(WifCompressed, WifUncompressed):
  BitCompressed = Key(WifCompressed)
  BitUnCompressed = Key(WifUncompressed)
  return BitCompressed.address, BitUnCompressed.address

def _LoadTargetFile(FileName):
  return {i.strip() for i in open(FileName).readlines()}

if __name__ == '__main__':
  target_file = '/content/blockchair_bitcoin_addresses_and_balance_LATEST.tsv'
  Target = _LoadTargetFile(FileName=target_file)

  worker = Worker(target_file, Target)
  worker.start()

  MainCheck(Target)
