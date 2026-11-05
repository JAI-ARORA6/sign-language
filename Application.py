# Importing Libraries
import numpy as np
import cv2
import os
import operator
from string import ascii_uppercase
import tkinter as tk
from PIL import Image, ImageTk
import enchant
from keras.models import model_from_json


class Application:
    def __init__(self):

        # Spell checker
        self.hs = enchant.Dict("en_US")

        # Camera
        self.vs = cv2.VideoCapture(0)
        if not self.vs.isOpened():
            print("Error: Camera not accessible")
            exit()

        self.current_image = None
        self.current_image2 = None

        # Load models (FIXED PATHS)
        self.loaded_model = model_from_json(open("Models/model_new.json").read())
        self.loaded_model.load_weights("Models/model_new.h5")

        self.loaded_model_dru = model_from_json(open("Models/model-bw_dru.json").read())
        self.loaded_model_dru.load_weights("Models/model-bw_dru.h5")

        self.loaded_model_tkdi = model_from_json(open("Models/model-bw_tkdi.json").read())
        self.loaded_model_tkdi.load_weights("Models/model-bw_tkdi.h5")

        self.loaded_model_smn = model_from_json(open("Models/model-bw_smn.json").read())
        self.loaded_model_smn.load_weights("Models/model-bw_smn.h5")

        print("Models Loaded Successfully")

        # Counters
        self.ct = {'blank': 0}
        self.blank_flag = 0
        for i in ascii_uppercase:
            self.ct[i] = 0

        # UI Setup
        self.root = tk.Tk()
        self.root.title("Sign Language To Text Conversion")
        self.root.geometry("900x900")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)
        self.panel.place(x=100, y=10, width=580, height=580)

        self.panel2 = tk.Label(self.root)
        self.panel2.place(x=400, y=65, width=275, height=275)

        self.panel3 = tk.Label(self.root)
        self.panel3.place(x=500, y=540)

        self.panel4 = tk.Label(self.root)
        self.panel4.place(x=220, y=595)

        self.panel5 = tk.Label(self.root)
        self.panel5.place(x=350, y=645)

        self.str = ""
        self.word = ""
        self.current_symbol = ""

        self.video_loop()

    # ================= VIDEO LOOP =================
    def video_loop(self):
        ok, frame = self.vs.read()

        if ok:
            frame = cv2.flip(frame, 1)

            x1 = int(0.5 * frame.shape[1])
            y1 = 10
            x2 = frame.shape[1] - 10
            y2 = int(0.5 * frame.shape[1])

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 1)

            roi = frame[y1:y2, x1:x2]

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 2)

            _, thresh = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            self.predict(thresh)

            # Display camera
            img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.panel.config(image=img)
            self.panel.image = img

            # Display processed image
            img2 = ImageTk.PhotoImage(Image.fromarray(thresh))
            self.panel2.config(image=img2)
            self.panel2.image = img2

            # Text display
            self.panel3.config(text=self.current_symbol, font=("Courier", 30))
            self.panel4.config(text=self.word, font=("Courier", 30))
            self.panel5.config(text=self.str, font=("Courier", 30))

        self.root.after(10, self.video_loop)

    # ================= PREDICTION =================
    def predict(self, img):
        img = cv2.resize(img, (128, 128))
        img = img.reshape(1, 128, 128, 1)

        result = self.loaded_model.predict(img)

        prediction = {'blank': result[0][0]}
        index = 1

        for i in ascii_uppercase:
            prediction[i] = result[0][index]
            index += 1

        prediction = sorted(prediction.items(), key=operator.itemgetter(1), reverse=True)
        self.current_symbol = prediction[0][0]

        self.ct[self.current_symbol] += 1

        if self.ct[self.current_symbol] > 40:

            for i in ascii_uppercase:
                self.ct[i] = 0

            if self.current_symbol == 'blank':
                self.str += " " + self.word
                self.word = ""
            else:
                self.word += self.current_symbol

    # ================= BUTTON ACTION =================
    def action1(self):
        suggestions = self.hs.suggest(self.word)
        if suggestions:
            self.str += " " + suggestions[0]
            self.word = ""

    # ================= CLOSE APP =================
    def destructor(self):
        print("Closing Application...")
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()


# Run app
print("Starting Application...")
(Application()).root.mainloop()