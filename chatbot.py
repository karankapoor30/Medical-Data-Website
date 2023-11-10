import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser
import os
import smtplib
engine=pyttsx3.init("sapi5")  
voices=engine.getProperty("voices") 
engine.setProperty("voice",voices[1].id)   

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def greetings():
    hour=int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning")
    elif hour>=12 and hour<16:
        speak("Good Afternoon")
    elif hour>=16 and hour<21:
        speak("Good Evening")
    else:
        speak("Good Night")
    speak("I am your personal medical assistant. how may I help you today.")

def takeCommand(): 
    r=sr.Recognizer()
    with sr.Microphone() as source: 
        print('Listening...')
        r.pause_threshold=1 
        audio=r.listen(source) 
    
    try: 
        print("Recognizing...")
        query=r.recognize_google(audio,language='en-in')
        print(query)

    except Exception as e: 
        print("please say that again...")
        return "None"
    return(query)

greetings()
while True:
    query=takeCommand().lower() 
    
    if "wikipedia" in query:
        speak("Searching Wikipedia")
        query=query.replace("wikipedia","")
        results=wikipedia.summary(query,sentences=2)
        speak("According to Wikipedia")
        print(results) 
        speak(results)
    
    elif "pain" in query:
        speak("Take Acetaminophen and hydocodone")

    elif "high blood pressure" in query:
        speak("take Metoprolol")

    elif "diabetes" in query:
        speak("take metformin")

    elif "high cholestrol" in query:
        speak("take Atorvastatin")

    elif "bodyache" in query:
        speak("take Ibuprofen")