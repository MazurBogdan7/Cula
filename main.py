import os
import requests
import openai
import feedparser
import random

# Загрузка конфигураций из файла config.env
from dotenv import load_dotenv
load_dotenv()

# Переменные окружения из config.env
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
GIPHY_API_KEY = os.getenv('GIPHY_API_KEY')

# Темы и теги
THEME_TAGS = {
    'space': '#астрономия',
    'astronauts': '#космонавтика',
    'brain': '#нейробиология',
    'math': '#математика',
}

# Новости
NEWS_FEEDS = [
    'https://www.nasa.gov/rss/dyn/breaking_news.rss',
    'https://www.nature.com/subjects/space-and-astronomy.rss',
    'https://www.sciencemag.org/rss/news_current.xml'
]

# Инициализация OpenAI
openai.api_key = OPENAI_API_KEY

# Функция для получения краткой сводки новости
def summarize_article(article_content):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Сделай краткую сводку новости: {article_content}",
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Функция для определения тега на основе содержания статьи
def get_news_tag(article_content):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Определи тематику новости и выбери подходящий тег: {', '.join(THEME_TAGS.keys())}. Текст новости: {article_content}",
        max_tokens=10
    )
    theme = response.choices[0].text.strip().lower()
    return THEME_TAGS.get(theme, '#наука')

# Функция для получения гифки через Giphy API
def get_gif_url(query):
    url = f"http://api.giphy.com/v1/gifs/search?api_key={GIPHY_API_KEY}&q={query}&limit=10"
    response = requests.get(url)
    data = response.json()
    if data['data']:
        gif_url = random.choice(data['data'])['images']['original']['url']
        return gif_url
    return None

# Функция для отправки сообщения с изображением в Telegram
def send_telegram_message(text, gif_url=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'  # Используем HTML форматирование
    }
    
    # Если есть gif или изображение
    if gif_url:
        # Отправляем сначала гифку или картинку
        media_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAnimation"
        media_payload = {
            'chat_id': CHAT_ID,
            'animation': gif_url,
        }
        requests.post(media_url, data=media_payload)

    # Затем отправляем текст сообщения
    response = requests.post(url, data=payload)
    return response

# Функция для обработки и отправки новостей
def process_and_send_news():
    for feed_url in NEWS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:3]:  # Берём только первые 3 новости
            title = entry.title
            link = entry.link
            summary = summarize_article(entry.summary)
            tag = get_news_tag(entry.summary)

            # Подбор гифки (запрос ключевого слова из заголовка)
            gif_url = get_gif_url(title)

            # Форматирование сообщения с использованием HTML
            message = (
                f"<b>{title}</b>\n\n"
                f"<a href='{link}'>{summary}</a>\n\n"
                f"⚡ <a href='https://t.me/sigma_naut'>Сигма | Научпоп</a>\n\n"
                f"{tag}"
            )

            # Отправка сообщения с гифкой
            send_telegram_message(message, gif_url)

if __name__ == "__main__":
    process_and_send_news()
