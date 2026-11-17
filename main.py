import os
import re
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta

CHANNEL_NAME = "happvpn"  # ваш канал
LAST_SENT_FILE = "last_sent.txt"

def fetch_latest_post(channel):
    url = f"https://t.me/s/{channel}"
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        
        messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
        if not messages:
            return None
        
        raw_msg = messages[-1]
        text = re.sub(r'<br\s*/?>', '\n', raw_msg)
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
    except Exception as e:
        print(f"❌ Ошибка при чтении канала {channel}: {e}")
        return None

def send_email(subject, body, to_emails, user, password):
    try:
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = to_emails
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            recipients = [e.strip() for e in to_emails.split(',')]
            server.sendmail(user, recipients, msg.as_string())
        print("✅ Письмо с новым постом успешно отправлено!")
    except Exception as e:
        print(f"❌ Ошибка при отправке письма: {e}")

def main():
    msk_tz = timezone(timedelta(hours=3))
    now_msk = datetime.now(msk_tz).strftime("%d.%m.%Y %H:%M")
    
    print(f"Проверяем канал: {CHANNEL_NAME}...")
    latest_post = fetch_latest_post(CHANNEL_NAME)
    
    if not latest_post:
        print("⚠️ Не удалось получить посты.")
        return

    # Читаем текст предыдущего отправленного поста
    previous_post = ""
    if os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE, "r", encoding="utf-8") as f:
            previous_post = f.read().strip()

    # Сравниваем
    if latest_post == previous_post:
        print("ℹ️ Новых постов нет (текст не изменился). Письмо не отправляется.")
    else:
        print("🔥 Обнаружен новый пост! Отправляем...")
        # Сохраняем новый текст
        with open(LAST_SENT_FILE, "w", encoding="utf-8") as f:
            f.write(latest_post)
        
        email_body = (
            f"Новый пост из канала @{CHANNEL_NAME} ({now_msk} МСК):\n\n"
            f"{latest_post}"
        )
        
        # Берем секреты из окружения GitHub
        gmail_user = os.environ.get("GMAIL_USER")
        gmail_pass = os.environ.get("GMAIL_PASS")
        
        if gmail_user and gmail_pass:
            recipients = "bayramsanazarow1997@gmail.com"
            send_email("Новый VPN пост из Telegram", email_body, recipients, gmail_user, gmail_pass)
        else:
            print("❌ Ошибка: не найдены секреты GMAIL_USER или GMAIL_PASS!")

    # Обновляем статус для активности репозитория
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write(f"Last check: {now_msk} MSK\n")

if __name__ == "__main__":
    main()
