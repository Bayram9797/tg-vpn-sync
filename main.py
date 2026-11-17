import os
import re
import urllib.request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta

CHANNEL_NAME = "happvpn"
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
        
        protocols = ["happ://", "vless://", "vmess://", "trojan://", "ss://", "hysteria2://", "tuic://"]
        for proto in protocols:
            text = re.sub(r'([^\s\n])(' + re.escape(proto) + ')', r'\1\n\2', text)
            
        return text.strip()
    except Exception as e:
        print(f"❌ Ошибка при чтении канала {channel}: {e}")
        return None

def send_email(subject, plain_body, html_body, to_emails, user, password):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = user
        msg['To'] = to_emails
        msg['Subject'] = subject
        
        # Добавляем обычную и HTML версию, чтобы почтовики отображали с переносами
        msg.attach(MIMEText(plain_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(user, password)
            recipients = [e.strip() for e in to_emails.split(',')]
            server.sendmail(user, recipients, msg.as_string())
        print("✅ Письмо успешно отправлено!")
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

    previous_post = ""
    if os.path.exists(LAST_SENT_FILE):
        with open(LAST_SENT_FILE, "r", encoding="utf-8") as f:
            previous_post = f.read().strip()

    if latest_post == previous_post:
        print("ℹ️ Новых постов нет (текст не изменился). Письмо не отправляется.")
    else:
        print("🔥 Обнаружен новый пост! Отправляем...")
        with open(LAST_SENT_FILE, "w", encoding="utf-8") as f:
            f.write(latest_post)
        
        # Текст для обычных клиентов
        plain_text = (
            f"Новый пост из канала @{CHANNEL_NAME} ({now_msk} МСК):\n\n"
            f"{latest_post}"
        )
        
        # HTML-версия: оборачиваем в тег <pre>, который заставляет почту сохранять все переносы строк и форматирование
        escaped_post = latest_post.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html_text = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <p><b>Новый пост из канала @{CHANNEL_NAME} ({now_msk} МСК):</b></p>
            <pre style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; word-break: break-all; font-family: monospace;">{escaped_post}</pre>
        </body>
        </html>
        """
        
        gmail_user = os.environ.get("GMAIL_USER")
        gmail_pass = os.environ.get("GMAIL_PASS")
        
        if gmail_user and gmail_pass:
            recipients = "bayramsanazarow1997@gmail.com"
            send_email("Новый VPN пост из Telegram", plain_text, html_text, recipients, gmail_user, gmail_pass)
        else:
            print("❌ Ошибка: не найдены секреты GMAIL_USER или GMAIL_PASS!")

    with open("status.txt", "w", encoding="utf-8") as f:
        f.write(f"Last check: {now_msk} MSK\n")

if __name__ == "__main__":
    main()
