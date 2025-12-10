import telebot
import requests
from datetime import datetime
import pytz

# Токены
TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"
WEATHER_API_KEY = "ВАШ_OPENWEATHER_API_KEY"

bot = telebot.TeleBot(TOKEN)

# Получение погоды для Казани
def get_kazan_weather():
    """Получает погоду в Казани"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q=Kazan&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("cod") != 200:
            return None
        
        # Время в Казани
        kazan_tz = pytz.timezone('Europe/Moscow')
        kazan_time = datetime.now(kazan_tz)
        
        # Парсим данные
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"] * 0.750062  # в мм рт.ст.
        wind_speed = data["wind"]["speed"]
        wind_direction = get_wind_direction(data["wind"].get("deg", 0))
        description = data["weather"][0]["description"]
        icon = get_weather_icon(data["weather"][0]["icon"])
        
        return {
            "temp": temp,
            "feels_like": feels_like,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "wind_direction": wind_direction,
            "description": description,
            "icon": icon,
            "time": kazan_time.strftime("%H:%M"),
            "date": kazan_time.strftime("%d.%m.%Y"),
            "full_time": kazan_time.strftime("%H:%M %d.%m.%Y")
        }
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def get_wind_direction(degrees):
    """Определяет направление ветра"""
    directions = ["С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ"]
    idx = round(degrees / 45) % 8
    return directions[idx]

def get_weather_icon(icon_code):
    """Возвращает emoji по коду погоды"""
    icons = {
        "01d": "☀️", "01n": "🌙",
        "02d": "⛅", "02n": "☁️",
        "03d": "☁️", "03n": "☁️",
        "04d": "☁️", "04n": "☁️",
        "09d": "🌧️", "09n": "🌧️",
        "10d": "🌦️", "10n": "🌧️",
        "11d": "⛈️", "11n": "⛈️",
        "13d": "❄️", "13n": "❄️",
        "50d": "🌫️", "50n": "🌫️"
    }
    return icons.get(icon_code, "🌤️")

# Команды бота
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 Привет! Я бот погоды Казани!\n\n"
        "Доступные команды:\n"
        "/weather - Погода в Казани сейчас\n"
        "/today - Подробный прогноз на сегодня\n"
        "/help - Помощь\n\n"
        "Или просто напиши 'Казань' или 'погода'"
    )
    
    # Создаем клавиатуру
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = telebot.types.KeyboardButton('🌤 Погода в Казани')
    btn2 = telebot.types.KeyboardButton('📍 Моя геолокация', request_location=True)
    btn3 = telebot.types.KeyboardButton('❓ Помощь')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['weather'])
def send_kazan_weather(message):
    """Погода в Казани сейчас"""
    weather = get_kazan_weather()
    
    if weather:
        text = (
            f"{weather['icon']} *Погода в Казани*\n\n"
            f"🌡 *Температура:* {weather['temp']:.1f}°C\n"
            f"🤔 *Ощущается как:* {weather['feels_like']:.1f}°C\n"
            f"💧 *Влажность:* {weather['humidity']}%\n"
            f"📊 *Давление:* {weather['pressure']:.0f} мм рт.ст.\n"
            f"💨 *Ветер:* {weather['wind_speed']} м/с, {weather['wind_direction']}\n"
            f"📝 *Описание:* {weather['description']}\n\n"
            f"🕐 *Время в Казани:* {weather['full_time']}"
        )
    else:
        text = "❌ Не удалось получить данные о погоде. Попробуйте позже."
    
    bot.send_message(message.chat.id, text, parse_mode='Markdown')

@bot.message_handler(commands=['today'])
def send_today_forecast(message):
    """Подробный прогноз на сегодня"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q=Kazan&appid={WEATHER_API_KEY}&units=metric&lang=ru&cnt=8"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get("cod") != "200":
            bot.send_message(message.chat.id, "❌ Не удалось получить прогноз.")
            return
        
        forecast_text = "📅 *Прогноз погоды в Казани на сегодня:*\n\n"
        
        for item in data["list"][:6]:  # Берем 6 периодов (каждые 3 часа)
            time = datetime.fromtimestamp(item["dt"]).strftime("%H:%M")
            temp = item["main"]["temp"]
            desc = item["weather"][0]["description"]
            icon = get_weather_icon(item["weather"][0]["icon"])
            
            forecast_text += f"⏰ *{time}*: {icon} {temp:.0f}°C, {desc}\n"
        
        bot.send_message(message.chat.id, forecast_text, parse_mode='Markdown')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "📖 *Помощь по боту:*\n\n"
        "*Команды:*\n"
        "/start - Начать работу\n"
        "/weather - Погода в Казани сейчас\n"
        "/today - Прогноз на сегодня\n"
        "/help - Эта справка\n\n"
        "*Как использовать:*\n"
        "• Нажмите кнопку '🌤 Погода в Казани'\n"
        "• Или напишите 'Казань', 'погода'\n"
        "• Или отправьте свою геолокацию\n\n"
        "*Данные:*\n"
        "Погода обновляется в реальном времени с OpenWeatherMap"
    )
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower()
    
    if any(word in text for word in ['казань', 'погода', 'weather', 'температура']):
        send_kazan_weather(message)
    elif 'прогноз' in text:
        send_today_forecast(message)
    elif 'помощь' in text or 'help' in text:
        send_help(message)
    else:
        bot.reply_to(message, 
                   "Я специализируюсь на погоде в Казани! 🌤\n"
                   "Напишите 'Казань' или нажмите кнопку ниже.")

# Обработка геолокации
@bot.message_handler(content_types=['location'])
def handle_location(message):
    if message.location:
        # Можно добавить сравнение с Казанью или показ погоды по координатам
        lat = message.location.latitude
        lon = message.location.longitude
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            response = requests.get(url)
            data = response.json()
            
            if data["cod"] == 200:
                city = data.get("name", "вашем городе")
                temp = data["main"]["temp"]
                
                bot.send_message(message.chat.id,
                               f"📍 По вашей геолокации:\n"
                               f"Вы в городе: {city}\n"
                               f"Температура: {temp}°C\n\n"
                               f"Хотите узнать погоду в Казани? Напишите 'Казань'")
        except:
            bot.send_message(message.chat.id,
                           "📍 Спасибо за геолокацию!\n"
                           "Хотите узнать погоду в Казани? Нажмите кнопку '🌤 Погода в Казани'")

# Запуск бота
print("Бот погоды Казани запущен...")
bot.polling(none_stop=True)