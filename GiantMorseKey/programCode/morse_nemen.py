#!/usr/bin/python3.9
import pygame as pygame
import time
import gpiozero as gpio
import tkinter as tk
from array import array
from pygame.locals import *
from morse_encode import *
from tkinter.filedialog import askopenfilename
from tkinter import scrolledtext
import sys
import _thread as thread
import random

pygame.mixer.pre_init(44100, -16, 1, 1024)
pygame.init()

class ToneSound(pygame.mixer.Sound):
    def __init__(self, frequency, volume):
        self.frequency = frequency
        pygame.mixer.Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    def build_samples(self):
        period = int(round(pygame.mixer.get_init()[0] / self.frequency))
        samples = array("h", [0] * period)
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        for time in range(period):
            if time < period / 2:
                samples[time] = amplitude
            else:
                samples[time] = -amplitude
        return samples

tone_obj = ToneSound(frequency = 800, volume = .5)

# default instelling seinsnelheid op 28 woorden per minuut
dot=0.05
dash=3*dot
gap=1*dot
lettergap=3*dot

# importeer morse encode tabel
encode=morse_code_encode

# lijst met letters en cijfers tbv random tekst generatie
letters_en_cijfers=("a","b","c","d","e","f","g","h","i","j",
                    "k","l","m","n","o","p","q","r","s","t",
                    "u","v","w","x","y","z","1","2","3","4",
                    "5","6","7","8","9","0")

# Tekst veld ininiteel leeg
tekst=""

# running of stop status van de start_nemen routine
running=True

# default tekstbron: tekstbestand en normale lettergap
# tekstbestand en normale lettergap: "1"
# tekst bestand en grote lettergap: "2"
# random characters en normale lettergap: "3"
# random characters en grote lettergap: "4"
tekstbron=("1")

def rand_char_normaal():
    global tekst
    global running

    tekst=""
    # genereer 40 random letters en cijfers in tekst
    for i in range(1,81):
        tekst=tekst+letters_en_cijfers[random.randint(0,
                                len(letters_en_cijfers)-1)]
        if i%5==0:
            tekst=tekst+(" ")
    running=True
    button_start.config(state="active")

def beep(sec):
    tone_obj.play(-1)
    time.sleep(sec)
    tone_obj.stop()
    return




def open_oefen_tekst():
    global tekst
    global running
    bestandsnaam=askopenfilename (filetypes=[("Tekst","*.txt"),("All Files","*.*")])
    file = open (bestandsnaam,"r")
    tekst = file.read()
    file.close()
    button_start.config(state="active")
    running=True
    return

def start_nemen():
    global dot
    global dash
    global gap
    global lettergap
    global encode
    global text_area
    global running

    button_start.config(state="disabled")
    button_open.config(state="disabled")
    button_genereer.config(state="disabled")
    button_stop.config(state="active")

    # neem de ingestelde seinsnelheid over
    w_p_m=wpm.get()
    if not w_p_m.isdecimal():
        w_p_m="15"
        wpm.insert(0,"15")
    dot=60/(int(w_p_m)*43)
    dash=3*dot
    gap=1*dot
    lettergap=3*dot

    for letter in tekst:
        if running==False:
            break
        if letter==" ":
            #text_area.update_idletasks() #
            time.sleep(7*dot)
        else:
            try:
                buffer=encode[letter]
            except KeyError:
                buffer="..--.."
            for key in buffer:
                if key==".":
                    beep(dot)
                else:
                    beep(dash)
                time.sleep(gap)
            time.sleep(lettergap)
            # diplay de laatse letter van de tekst
        text_area.insert("end",letter)
        #text_area.update_idletasks()
        text_area.see("end")
    running=True
    return

def startthread_nemen():
    thread.start_new_thread(start_nemen, ())
    return

def stop_nemen():
    global running
    running=False
    button_start.config(state="active")
    button_stop.config(state="disabled")
    button_open.config(state="active")
    button_genereer.config(state="active")
    return

window=tk.Tk()
window.title("Oefenprogramma Morse Nemen")

window.columnconfigure([0,1,2,3,4,5],minsize=20)
window.rowconfigure([0,1,2,3,4,5,6], minsize=20)

label_ssh=tk.Label(text="Seinsnelheid in wpm:")
label_ssh.grid(row=0,column=1,columnspan=2,sticky="w")

wpm=tk.Entry(width=2)
wpm.grid(row=1,column=2,sticky="w")
wpm.insert(0, "15")

button_genereer=tk.Button(text="Genereer oefen tekst",command=rand_char_normaal)
button_genereer.grid(row=2,column=2)

button_open=tk.Button(text="Kies oefen tekst",command=open_oefen_tekst)
button_open.grid(row=2,column=3)

button_start=tk.Button(text="Start oefening",command=startthread_nemen)
button_start.grid(row=3,column=3)

button_stop=tk.Button(text="Stop oefening",command=stop_nemen)
button_stop.grid(row=4,column=3)

button_open.config(state="active")
button_genereer.config(state="active")
button_start.config(state="disabled")
button_stop.config(state="disabled")

text_area = scrolledtext.ScrolledText(window, wrap = tk.WORD,font = ("Times New Roman", 15))
text_area.grid(row=5,column=2,columnspan=3)

window.mainloop()
