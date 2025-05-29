import tkinter as tk
from tkinter import ttk
import threading
import datetime
import random
import time
import json
import pyttsx3
import speech_recognition as sr
import os
import pyautogui
import webbrowser
import wikipedia
import schedule
import logging
import cv2
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import requests
from tkinter.filedialog import askopenfilename
from textwrap import shorten

MEMORY_FILE = "glizzy_memory.json"
WAKE_WORD = "glizzy"
MUSIC_FOLDER = "music"
LOG_FILE = "glizzy_log.txt"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s: %(message)s')

class GlizzyGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.memory = self.load_memory()
        self.mood = self.memory.get("mood", "curious")
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.title("ASSISTANT GLIZZY")
        self.configure(bg="#0a0a0a")
        self.attributes('-fullscreen', True)

        # Techy border frame
        self.main_frame = tk.Frame(self, bg="#111", highlightbackground="#0ff", highlightthickness=4)
        self.main_frame.grid(row=0, column=0, padx=40, pady=40, rowspan=5, sticky="nsew")

        # Wolf ASCII Banner
        wolf_banner = """
 
      <>              
    .::::.             
@\|/W\/\/W\|/@         
 \|/^\/\/^\|/     
  \_O_<>_O_/


        """
         
        
        self.banner_label = tk.Label(self.main_frame, text=wolf_banner, font=("Consolas", 18, "bold"),
                                     fg="#0ff", bg="#111", justify="left")
        self.banner_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))

        self.mood_label = self.create_label(f"Mood: {self.mood.title()} 🐺", 1)
        self.time_label = self.create_label("", 2)
        self.response_box = self.create_textbox(3)
        self.input_entry = self.create_input_entry(4)

        # Neon wolf face canvas
        self.face_canvas = tk.Canvas(self.main_frame, width=300, height=300, bg="#111", highlightthickness=0)
        self.face_canvas.grid(row=0, column=1, rowspan=5, padx=30, pady=10)
        self.animate_wolf()

        # Add a glowing effect to the input box
        self.input_entry.config(highlightbackground="#0ff", highlightcolor="#0ff", highlightthickness=2, relief="flat")

        # Blinking cursor effect
        self.blink_cursor()

        self.animate_terminal("SYSTEM ONLINE // Welcome, Commander.")
        self.speak("Welcome, Commander. How can I assist you today?")
        self.update_clock()

        self.schedule_thread = threading.Thread(target=self.schedule_check, daemon=True)
        self.schedule_thread.start()

    def load_memory(self):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {"facts": {}, "custom_commands": {}, "context": {}, "mood": "curious", "voice": {}}

    def save_memory(self):
        with open(MEMORY_FILE, "w") as f:
            json.dump(self.memory, f, indent=2)

    def speak(self, text):
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if "India" in voice.name and "Female" in voice.name:
                self.engine.setProperty('voice', voice.id)
                break
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            return self.recognizer.recognize_google(audio).lower()
        except:
            return None

    def create_label(self, text, row):
        label = tk.Label(self.main_frame, text=text, font=("Consolas", 18, "bold"),
                         fg="#0ff", bg="#111")
        label.grid(row=row, column=0, sticky="w", padx=10, pady=5)
        return label

    def create_textbox(self, row):
        text_widget = tk.Text(self.main_frame, height=18, width=90, bg="#181818", fg="#39ff14",
                              font=("Cascadia Mono", 15, "bold"), borderwidth=0, insertbackground="#39ff14")
        text_widget.grid(row=row, column=0, padx=10, pady=10)
        text_widget.insert("end", "[GLIZZY]: Initializing systems...\n")
        text_widget.config(state="disabled")
        return text_widget

    def create_input_entry(self, row):
        entry = tk.Entry(self.main_frame, font=("Cascadia Mono", 16, "bold"), width=80,
                         bg="#111", fg="#39ff14", insertbackground="#39ff14", relief="flat")
        entry.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        entry.bind("<Return>", lambda e: self.process_input(entry.get()))
        return entry

    def blink_cursor(self):
        # Blinking effect for the input entry cursor
        def blink():
            current = self.input_entry.cget("insertbackground")
            new_color = "#111" if current == "#39ff14" else "#39ff14"
            self.input_entry.config(insertbackground=new_color)
            self.after(500, blink)
        blink()

    def animate_wolf(self):
        # Neon wolf face
        steps = [
            (150, 50, 150, 80),
            (120, 100, 180, 100),
            (100, 120, 200, 120),
            (120, 160, 180, 160),
            (130, 200, 170, 200),
            (110, 250, 190, 250)
        ]
        colors = ["#0ff", "#39ff14", "#f0f", "#0ff", "#39ff14", "#f0f"]

        def draw_step(i=0):
            if i < len(steps):
                self.face_canvas.create_line(*steps[i], fill=colors[i], width=4, capstyle=tk.ROUND)
                self.after(180, lambda: draw_step(i+1))

        draw_step()

    def update_clock(self):
        now = datetime.datetime.now().strftime("%A, %d %B %Y | %H:%M:%S")
        self.time_label.config(text=f"System Time: {now}")
        self.after(1000, self.update_clock)

    def animate_terminal(self, message):
        def animate():
            self.response_box.config(state="normal")
            for char in f"[Glizzy]: {message}\n":
                self.response_box.insert("end", char)
                self.response_box.see("end")
                self.response_box.update()
                time.sleep(0.02)
            self.response_box.config(state="disabled")

        threading.Thread(target=animate).start()

    def schedule_check(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

    def log_command(self, cmd):
        logging.info(cmd)

    def fetch_google_summary(self, query):
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(f"https://www.google.com/search?q={query}", headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            answer = soup.find("div", class_="BNeawe").text
            return answer
        except:
            return "Couldn't fetch anything from Google."

    def summarize_text(self, text, max_words=50):
        return shorten(text, width=max_words*6, placeholder="...")

    def detect_face_and_mood(self):
        cam = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        detected = False
        for _ in range(30):
            ret, frame = cam.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) > 0:
                detected = True
                break
        cam.release()
        self.memory["mood"] = "happy" if detected else "tired"
        self.save_memory()
        return "Face detected! You're here." if detected else "No face detected."

    def read_pdf(self):
        self.withdraw()
        filepath = askopenfilename(filetypes=[("PDF files", "*.pdf")])
        self.deiconify()
        if not filepath: return "No file selected."
        doc = fitz.open(filepath)
        text = " ".join([page.get_text() for page in doc])
        summary = self.summarize_text(text)
        self.speak("Here's the summary of the PDF.")
        return summary

    def play_music(self):
        if not os.path.exists(MUSIC_FOLDER):
            os.makedirs(MUSIC_FOLDER)
        songs = [s for s in os.listdir(MUSIC_FOLDER) if s.endswith('.mp3')]
        if not songs:
            return "No music found in the music folder."
        os.startfile(os.path.join(MUSIC_FOLDER, random.choice(songs)))
        return "Playing music."

    def mood_response(self, text):
        mood = self.memory.get("mood", "neutral")
        if mood == "happy": return f"😊 Yay! {text}"
        if mood == "grumpy": return f"😒 Ugh. {text}"
        if mood == "curious": return f"🤔 Interesting... {text}"
        if mood == "tired": return f"😴 I'm tired but... {text}"
        return text

    def process_input(self, user_input):
        self.input_entry.delete(0, "end")
        self.memory["context"]["last_command"] = user_input
        self.save_memory()
        self.log_command(user_input)

        command = user_input.lower()

        # Custom commands
        for cmd, val in self.memory["custom_commands"].items():
            if cmd.lower() == command:
                self.respond(val)
                return

        # Facts
        for key, val in self.memory["facts"].items():
            if key.lower() in command:
                self.respond(val)
                return

        # Memory
        if "remember that" in command:
            try:
                fact = command.replace("remember that", "").strip()
                key, value = fact.split(" is ", 1)
                self.memory["facts"][key.strip()] = value.strip()
                self.save_memory()
                self.respond(f"Got it. I will remember that {key} is {value}.")
            except:
                self.respond("Sorry, I couldn't understand what to remember.")
            return

        # Wikipedia
        elif "search wikipedia" in command:
            topic = command.replace("search wikipedia", "").strip()
            try:
                summary = wikipedia.summary(topic, sentences=2)
                self.respond(summary)
            except:
                self.respond("Couldn't find it on Wikipedia.")
            return

        # Google
        elif "search google for" in command:
            query = command.replace("search google for", "").strip()
            summary = self.fetch_google_summary(query)
            self.respond(summary)
            return

        # Play music
        elif "play music" in command:
            self.respond(self.play_music())
            return

        # Summarize text
        elif "summarize this" in command:
            self.respond("Paste the text you want summarized in the terminal.")
            text = input("Text: ")
            self.respond(self.summarize_text(text))
            return

        # Read PDF
        elif "read pdf" in command:
            self.respond(self.read_pdf())
            return

        # Face/mood detection
        elif "check face" in command or "detect mood" in command:
            self.respond(self.detect_face_and_mood())
            return

        # Set reminder
        elif "set a reminder to" in command:
            task = command.replace("set a reminder to", "").strip()
            schedule.every(1).minutes.do(lambda: self.respond(f"Reminder: {task}"))
            self.respond(f"Reminder set for: {task}")
            return

        # Mood change
        elif "change your mood to" in command:
            new_mood = command.replace("change your mood to", "").strip()
            self.memory["mood"] = new_mood
            self.save_memory()
            self.mood_label.config(text=f"Mood: {new_mood.title()} 🤖")
            self.respond(f"Mood changed to {new_mood}.")
            return

        elif "what's your mood" in command:
            self.respond(f"I'm currently feeling {self.memory.get('mood', 'neutral')}")
            return

        elif "what can you do" in command:
            self.respond("I can chat, play music, detect faces, read PDFs, summarize text, control volume, remember things, take reminders, and more.")
            return

        # Open websites
        elif "open" in command:
            if "youtube" in command:
                webbrowser.open("https://youtube.com")
                self.respond("Opening YouTube.")
            elif "instagram" in command:
                webbrowser.open("https://instagram.com")
                self.respond("Opening Instagram.")
            elif "google" in command:
                webbrowser.open("https://google.com")
                self.respond("Opening Google.")
            elif "facebook" in command:
                webbrowser.open("https://facebook.com")
                self.respond("Opening Facebook.")
            elif "twitter" in command:
                webbrowser.open("https://twitter.com")
                self.respond("Opening Twitter.")
            elif "reddit" in command:
                webbrowser.open("https://reddit.com")
                self.respond("Opening Reddit.")
            
            return

        # Typing
        elif "type" in command:
            text = command.replace("type", "").strip()
            pyautogui.write(text)
            self.respond(f"Typed: {text}")
        elif "write" in command:
            text = command.replace("write", "").strip()
            return

        # Volume
        elif "volume up" in command:
            pyautogui.press("volumeup")
            self.respond("Volume increased.")
            return

        elif "volume down" in command:
            pyautogui.press("volumedown")
            self.respond("Volume decreased.")
            return

        # Screenshot
        elif "screenshot" in command:
            file = f"screenshot_{int(time.time())}.png"
            pyautogui.screenshot(file)
            self.respond(f"Screenshot saved as {file}.")
            return

        # Exit
        elif "exit" in command:
            self.respond("Goodbye, Commander.")
            self.destroy()
            return

        # Learning new commands
        else:
            self.respond("I don't know this yet. Want me to learn it?")
            confirmation = self.listen() or input("Confirm learning (yes/no): ")
            if confirmation and "yes" in confirmation:
                self.respond("Tell me what I should reply.")
                response = self.listen() or input("Type your response: ")
                if response:
                    self.memory["custom_commands"][command] = response
                    self.save_memory()
                    self.respond("Learned it!")
                else:
                    self.respond("Okay, not learning it.")
            else:
                self.respond("Okay, not learning it.")
            # Optionally, you can implement a popup for learning new commands

    def respond(self, text):
        self.animate_terminal(self.mood_response(text))
        self.speak(text)

if __name__ == "__main__":
    app = GlizzyGUI()
    app.mainloop()