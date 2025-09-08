import requests
import time
import datetime
from flask import Flask
import threading

# === CONFIGURATION ===
TMDB_API_KEY = "41ee980e4b5f05f6693fda00eb7c4fd4"  # TMDb API Key
TELEGRAM_BOT_TOKEN = "8404826072:AAEySJWRKnLErIPSHTFy0hxQhosxh7p5Tvo"  # From BotFather
TELEGRAM_CHANNEL = "@republic_gamerz"  # Telegram channel username
MOVIX_URL = "https://movix.rf.gd"
AFFILIATE_LINK = "https://t.me/luciddreams?start=_tgr_ypKC6RNkZmNl"

# TMDb API endpoint for trending movies
TMDB_URL = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"

# Store posted movie IDs to avoid duplicates
posted_movies = set()
last_reset_day = datetime.date.today()

def get_trending_movies():
    """Fetch trending movies from TMDb"""
    response = requests.get(TMDB_URL)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

def send_to_telegram(movie):
    """Send movie details to Telegram channel"""
    title = movie.get("title")
    overview = movie.get("overview")
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

    # Telegram message content
    message = f"🎬 <b>{title}</b>\n\n{overview}\n\n🍿 Watch here: {MOVIX_URL}"

    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "photo": poster_url,
        "caption": message,
        "parse_mode": "HTML"
    }

    requests.post(telegram_api, data=payload)

def send_affiliate_link():
    """Send the affiliate link to Telegram channel"""
    message = f"🔥 Don't miss out! Join here: {AFFILIATE_LINK}"
    telegram_api = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(telegram_api, data=payload)

def reset_daily_posted_movies():
    """Reset posted movies list every new day"""
    global posted_movies, last_reset_day
    today = datetime.date.today()
    if today != last_reset_day:
        posted_movies.clear()
        last_reset_day = today
        print("🔄 Daily reset completed! Starting fresh movies list.")

def main():
    last_affiliate_post = time.time()

    while True:
        # Reset movie list if a new day starts
        reset_daily_posted_movies()

        # Fetch trending movies
        movies = get_trending_movies()
        posted_count = 0

        # Post 3 movies that haven't been posted yet
        for movie in movies:
            movie_id = movie.get("id")
            if movie_id not in posted_movies:
                send_to_telegram(movie)
                posted_movies.add(movie_id)
                posted_count += 1
                time.sleep(5)  # Delay to avoid Telegram flood limit

                # Stop after posting 3 movies per 30 minutes
                if posted_count >= 3:
                    break

        # Log status
        if posted_count > 0:
            print(f"✅ Posted {posted_count} new movies!")
        else:
            print("⚠️ No new movies found to post!")

        # Post affiliate link every 1 hour
        if time.time() - last_affiliate_post >= 3600:
            send_affiliate_link()
            last_affiliate_post = time.time()
            print("🔗 Affiliate link posted!")

        # Wait 30 minutes before next movie batch
        time.sleep(1800)

# === FLASK SERVER FOR RENDER / REPLIT ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Movie Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    main()
