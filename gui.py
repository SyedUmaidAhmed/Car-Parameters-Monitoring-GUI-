import tkinter as tk
from tkinter import font  as tkfont
import PIL
import smtplib
import threading
from PIL import Image,ImageTk, ImageSequence
from tkinter import messagebox, Label
from mpu6050 import mpu6050
import time
mpu = mpu6050(0x68, bus=1)
LARGE_FONT= ("Verdana", 12)
from scipy.spatial import distance as dist
from imutils.video import VideoStream
from imutils import face_utils
from threading import Thread
import numpy as np
import playsound
import argparse
import imutils
import dlib
import cv2
import pygame
import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)

global COUNTER, ALARM_ON

#Email Variables
SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
SMTP_PORT = 587 #Server Port (don't change!)
GMAIL_USERNAME = 'piwork99@gmail.com' #change this to match your gmail account
GMAIL_PASSWORD = 'ilovepis'  #change this to match your gmail password

pygame.mixer.init()
pygame.mixer.music.load('/home/pi/alarm.wav')
trigpin = [23,19]
echopin = [24,13]

for j in range(2):
    GPIO.setup(trigpin[j], GPIO.OUT)
    GPIO.setup(echopin[j], GPIO.IN)
    print (j, echopin[j], trigpin[j])


def sound_alarm(path):
    playsound.playsound(path)


def ping(echo, trig):

    GPIO.output(trig, False)
    # Allow module to settle
    time.sleep(0.5)
    # Send 10us pulse to trigger
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
    pulse_start = time.time()

    # save StartTime
    while GPIO.input(echo) == 0:
        pulse_start = time.time()

    # save time of arrival
    while GPIO.input(echo) == 1:
        pulse_end = time.time()

    # time difference between start and arrival
    pulse_duration = pulse_end - pulse_start
    # mutiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = pulse_duration * 17150

    distance = round(distance, 2)

    return distance






def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])

    ear = (A + B) / (2.0 * C)

    return ear

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--shape-predictor", required=False,
    help="path to facial landmark predictor")
ap.add_argument("-a", "--alarm", type=str, default="alarm.wav",
    help="path alarm .WAV file")
ap.add_argument("-w", "--webcam", type=int, default=0,
    help="index of webcam on system")
args = vars(ap.parse_args())

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 48

COUNTER = 0
ALARM_ON = False

print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('/home/pi/shape_predictor_68_face_landmarks.dat')

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

vs = VideoStream(src=args["webcam"]).start()
time.sleep(1.0)

class Emailer:
    def sendmail(self, recipient, subject, content):

        #Create Headers
        headers = ["From: " + GMAIL_USERNAME, "Subject: " + subject, "To: " + recipient,
                   "MIME-Version: 1.0", "Content-Type: text/html"]
        headers = "\r\n".join(headers)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Login to Gmail
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send Email & Exit
        session.sendmail(GMAIL_USERNAME, recipient, headers + "\r\n\r\n" + content)
        session.quit

sender = Emailer()








class CarGUI(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.attributes("-fullscreen",True)


        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand = True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageOne, PageTwo):

            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):


    def goTopageOne(self,data=None):
        self.controller.show_frame("PageOne")


    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        self.controller = controller

        global button_script, canvas


        canvas = tk.Canvas(self, bg= "white", width=1024,height=600)
        canvas.pack(fill=tk.BOTH, expand=tk.YES)

        back_g = Image.open('/home/pi/Car/bg.jpg')
        canvas.image_back_g =ImageTk.PhotoImage(back_g)
        back_g = canvas.create_image(0,0, image=canvas.image_back_g, anchor='nw')

        arrow = Image.open('/home/pi/Car/arrow.jpg')
        canvas.image_arrow =ImageTk.PhotoImage(arrow)
        arrow = canvas.create_image(800,60, image=canvas.image_arrow, anchor='nw')

        temp = Image.open('/home/pi/Car/temp.png')
        canvas.image_temp =ImageTk.PhotoImage(temp)
        temp = canvas.create_image(20,220, image=canvas.image_temp, anchor='nw')

        def apna_hurry(data=None):
            sendTo = 'syedumaidahmed96@gmail.com'
            emailSubject = "Emergency Press Detected!"
            emailContent = "The button has been pressed at: " + time.ctime()
            sender.sendmail(sendTo, emailSubject, emailContent)
            print("Email Sent")




        emerg = Image.open('/home/pi/Car/emer.jpg')
        canvas.image_emerg =ImageTk.PhotoImage(emerg)
        emerg = canvas.create_image(770,340, image=canvas.image_emerg, anchor='nw')
        canvas.tag_bind(emerg,"<Button-1>",apna_hurry)



        button_script = canvas.create_text(30,510, text="Starting", font="Times 40 bold",fill="#FFFFFF", anchor='nw')
        canvas.create_text(280,510, text="RPM: ", font="Times 50 bold",fill="#FFFFFF", anchor='nw')


        xts = canvas.create_text(45,30,fill="white",font="Times 30 bold italic",text="X:")
        xts_1 = canvas.create_text(125,45,fill="white",font="Times 30 bold",text="00")

        yts = canvas.create_text(45,90,fill="white",font="Times 30 bold italic",text="Y:")
        yts_1 = canvas.create_text(125,105,fill="white",font="Times 30 bold",text="00")

        zts = canvas.create_text(45,160,fill="white",font="Times 30 bold italic",text="Z:")
        zts_1 = canvas.create_text(125,175,fill="white",font="Times 30 bold",text="00")


        dist_1 = canvas.create_text(900,30,fill="white",font="Arial 30 bold",text="00")
        dist_2 = canvas.create_text(900,288,fill="white",font="Arial 30 bold",text="00")

        canvas.create_text(75,395,fill="white",font="Arial 20 bold",text="Temp: ")

        Temp = canvas.create_text(150,400,fill="white",font="Arial 15 bold italic",text=" ")






        lmain = Label(canvas)
        lmain.pack()

        def script(self):
            print("HELLO !")

            def show_fram():
                canvas.itemconfigure(xts_1, text=text1)
                canvas.itemconfigure(yts_1, text=text2)
                canvas.itemconfigure(zts_1, text=text3)
                canvas.itemconfigure(dist_1, text=forw)
                canvas.itemconfigure(dist_2, text=backw)
                canvas.itemconfigure(Temp, text=climate)


                global COUNTER, ALARM_ON
                frame = vs.read()
                frame = imutils.resize(frame, width=450)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                rects = detector(gray, 0)
                for rect in rects:
                    shape = predictor(gray, rect)
                    shape = face_utils.shape_to_np(shape)
                    leftEye = shape[lStart:lEnd]
                    rightEye = shape[rStart:rEnd]
                    leftEAR = eye_aspect_ratio(leftEye)
                    rightEAR = eye_aspect_ratio(rightEye)
                    ear = (leftEAR + rightEAR) / 2.0
                    leftEyeHull = cv2.convexHull(leftEye)
                    rightEyeHull = cv2.convexHull(rightEye)
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                    if ear < EYE_AR_THRESH:
                        COUNTER += 1
                        if COUNTER >= EYE_AR_CONSEC_FRAMES:
                            if not ALARM_ON:
                                ALARM_ON = True
                                if args["alarm"] != "":
                                    pygame.mixer.music.play()
                                    while pygame.mixer.music.get_busy() == True:
                                        continue
                        cv2.putText(frame, "DROWSINESS ALERT!", (10, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    else:
                        COUNTER = 0
                        ALARM_ON = False
                    cv2.putText(frame, "EAR: {:.2f}".format(ear), (300, 30),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                img = PIL.Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                lmain.imgtk = imgtk
                lmain.configure(image=imgtk)
                lmain.place(x=290,y=0)
                lmain.after(1000, show_fram)
            show_fram()

        canvas.tag_bind(button_script,"<Button-1>",script)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

    def goTopageTwo(self,data=None):
        self.controller.show_frame("PageTwo")





class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)




class myThread (threading.Thread):
    def run(self):
        global text1, text2, text3, forw, backw, climate
        while True:
            results = str(datetime.now()) + ","
            for j in range(2):

                distance = ping(echopin[j], trigpin[j])
                print ("sensor", j+1,": ",distance,"cm")
                if j==1:
                    forw  = distance
                else:
                    backw = distance
#            time.sleep(1)

            print("Temp : "+str(mpu.get_temp()))
            print()
            climate = mpu.get_temp()
            climate = round(climate,3)

            accel_data = mpu.get_accel_data()
            print("Acc X : "+str(accel_data['x']))
            print("Acc Y : "+str(accel_data['y']))
            print("Acc Z : "+str(accel_data['z']))
            print()


            gyro_data = mpu.get_gyro_data()
            print("Gyro X : "+str(gyro_data['x']))

            print("Gyro Y : "+str(gyro_data['y']))

            print("Gyro Z : "+str(gyro_data['z']))

            print()
            print("-------------------------------")

            text1=(gyro_data['x'])
            text1 = round(text1,3)

            text2=(gyro_data['y'])
            text2 = round(text2,3)

            text3=(gyro_data['z'])
            text3 = round(text3,3)




            time.sleep(1)

if __name__ == "__main__":
    thread1 = myThread()
    thread1.start()
    app = CarGUI()
    app.mainloop()