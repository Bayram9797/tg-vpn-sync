import os
import re
import urllib.request
from datetime import datetime, timezone, timedelta

# 👇 Укажите здесь ваш канал (без @) 👇
CHANNEL_NAME = "happvpn"  # замените на нужный, если это другой канал

def fetch_channel_posts(channel):
    url = f"https://t.me/s/{channel}"
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="replace")
        
        # Извлекаем блоки постов из веб-версии Telegram
        messages = re.findall(r'<div class="tgme_widget_message_text[^>]*>(.*?)</div>', html, re.DOTALL)
        
        clean_posts = []
        for msg in messages:
            # Убираем HTML-теги, но сохраняем структуру текста и переносы строк
            text = re.sub(r'<br\s*/?>', '\n', msg)
            text = re.sub(r'<[^>]+>', '', text)
            text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
            clean_posts.append(text.strip())
            
        return clean_posts
    except Exception as e:
        print(f"❌ Ошибка при чтении канала {channel}: {e}")
        return []

def main():
    msk_tz = timezone(timedelta(hours=3))
    now_msk = datetime.now(msk_tz).strftime("%d.%m.%Y %H:%M")
    
    os.makedirs("subs", exist_ok=True)
    
    print(f"Читаем посты из канала: {CHANNEL_NAME}...")
    posts = fetch_channel_posts(CHANNEL_NAME)
    
    if posts:
        # Берем последние посты (например, последние 3-5 штук, чтобы не захламлять)
        recent_posts = posts[-5:] 
        
        separator = "\n\n" + "="*40 + "\n\n"
        full_content = (
            f"=== Сводка из Telegram-канала @{CHANNEL_NAME} ===\n"
            f"Время обновления: {now_msk} (МСК)\n"
            f"{'='*40}\n\n"
        )
        full_content += separator.join(recent_posts)
        
        filepath = os.path.join("subs", "telegram_posts.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"✅ Успешно сохранено постов: {len(recent_posts)}")
    else:
        print("⚠️ Не удалось получить посты из канала.")
        filepath = os.path.join("subs", "telegram_posts.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Проверка от {now_msk}: посты не найдены или канал недоступен.")

    with open("status.txt", "w", encoding="utf-8") as f:
        f.write(f"Last tg sync: {now_msk} MSK\n")

if __name__ == "__main__":
    main()
