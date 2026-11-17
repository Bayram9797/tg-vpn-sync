import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta

CHANNEL_NAME = "happvpn"  # ваш канал
LAST_SENT_FILE = "last_sent.txt"
EMAIL_BODY_FILE = "email_body.txt"

def fetch_latest_post(channel):
    url = f"https://t.me/s/{channel}"
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        
        # Извлекаем все тексты постов
        messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
        if not messages:
            return None
        
        # Берем самый последний (самый свежий) пост из конца списка
        raw_msg = messages[-1]
        text = re.sub(r'<br\s*/?>', '\n', raw_msg)
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return text.strip()
    except Exception as e:
        print(f"❌ Ошибка при чтении канала {channel}: {e}")
        return None

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

    # Сравниваем свежий пост с прошлым отправленным
    if latest_post == previous_post:
        print("ℹ️ Новых постов нет (текст не изменился). Письмо отправляться не будет.")
        # Удаляем файл тела письма, чтобы GitHub Actions понял, что отправку нужно пропустить
        if os.path.exists(EMAIL_BODY_FILE):
            os.remove(EMAIL_BODY_FILE)
    else:
        print("🔥 Обнаружен новый пост! Подготавливаем к отправке.")
        # Сохраняем новый текст как последний отправленный
        with open(LAST_SENT_FILE, "w", encoding="utf-8") as f:
            f.write(latest_post)
        
        # Записываем текст для тела письма
        email_content = (
            f"Новый пост из канала @{CHANNEL_NAME} ({now_msk} МСК):\n\n"
            f"{latest_post}"
        )
        with open(EMAIL_BODY_FILE, "w", encoding="utf-8") as f:
            f.write(email_content)

    # Обновляем статус для активности репозитория
    with open("status.txt", "w", encoding="utf-8") as f:
        f.write(f"Last check: {now_msk} MSK\n")

if __name__ == "__main__":
    main()
