import os
import requests
import speech_recognition as sr
from gtts import gTTS
import playsound
from datetime import datetime
from groq import Groq

# Set up API Keys
GROQ_API_KEY = ""  # Replace with your Groq API key
OPENWEATHER_API_KEY = ""  # Replace with your OpenWeather API key
NEWSAPI_KEY = ""
# Initialize Groq Client
client = Groq(api_key=GROQ_API_KEY)

# Function to recognize speech from the microphone
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
            return None
        except sr.RequestError:
            print("Could not request results, please check your internet connection.")
            return None

# Function to get response from Groq API
def get_groq_response(user_input):
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            model="llama-3.3-70b-versatile",  # Use the correct model
            stream=False,
        )

        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"API Error: {str(e)}"

# Function to convert text to speech
def speak_response(response_text):
    tts = gTTS(text=response_text, lang="en")
    filename = "response.mp3"
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# Function to get the user's city automatically using IP
def get_city_from_ip():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        city = data.get("city", "Unknown location")
        return city
    except Exception as e:
        return "Unknown location"

# Function to get current date and time
def get_date_time():
    now = datetime.now()
    date = now.strftime("%A, %B %d, %Y")  # Example: Monday, February 8, 2025
    time = now.strftime("%I:%M %p")  # Example: 10:30 AM
    return date, time

# Function to fetch weather data from OpenWeather API


def get_news_from_pakistan():
    """Fetch latest news from Pakistan using NewsAPI.ai"""
    url = f"https://newsapi.ai/v2/top-headlines?country=pk&apiKey={NEWSAPI_KEY}"
    response = requests.get(url)
    
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get("articles", [])
        headlines = [article['title'] for article in articles]
        return headlines
    else:
        return ["Unable to fetch news. Please try again later."]



def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            temperature = data["main"]["temp"]
            weather_desc = data["weather"][0]["description"].capitalize()
            return f"The current temperature in {city} is {temperature}°C with {weather_desc}."
        else:
            return "Sorry, I couldn't fetch the weather data."
    except Exception as e:
        return "Error fetching weather data."

# Function to greet the user with date, time, and weather
def greet_user():
    city = get_city_from_ip()  # Automatically detect the user's city
    date, time = get_date_time()
    weather_info = get_weather(city)
    
    greeting_message = f"Hello! Welcome to your voice-activated chatbot. Today is {date}, and the time is {time}. {weather_info}. You can start speaking now. Say 'exit' to stop."
    
    print(greeting_message)
    speak_response(greeting_message)

# Main chatbot function
def voice_chatbot():
    greet_user()  # Greet the user with date, time, and weather
    
    print("Voice-Activated Chatbot Initialized. Say 'exit' to stop.")
    
    while True:
        user_text = recognize_speech()
        if user_text:
            if user_text.lower() in ["exit", "quit", "stop"]:
                farewell_message = "Goodbye! Have a great day."
                print(farewell_message)
                speak_response(farewell_message)
                break
            bot_response = get_groq_response(user_text)
            print(f"Chatbot: {bot_response}")
            speak_response(bot_response)

# Run the chatbot
if __name__ == "__main__":
    voice_chatbot()
