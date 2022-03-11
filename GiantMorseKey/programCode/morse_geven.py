#!/usr/bin/python3.9
import pygame
import time
import RPi.GPIO as GPIO
import sys
import tkinter as tk
from array import array
from pygame.locals import *

#   Dit gedeelte regelt de beep tijdens het keyen van de morse codes

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

#________________________________________________________________________________
# Basis van het programma zijn de volgende twee waarden:

dot=0.25 # dit is een vaste grenswaarde voor seinsnelheden tussen 6 wpm en 15 wpm
         # voor andere seinsnelheden werkt deze instelling niet!!
#  6 woorden per minuut betekent een dit van 0.230
# 10 wooreen per minuut betekent een dit van 0.139 (139 miliseconden)
# 15                                         0.093
# 20                                         0.069
# 25                                         0.057


# een beep die korter is dan een dot is een dit
# een beep die langer is dan een dot is een dash

chgap=0.3 # dit is een vaste grenswaarde rekening houdend met de seinsleutel-traagheid

# een stilte langer chgap is het begin van een nieuwe letter (lettergap) 
# een stilte kleiner/gelijk chgap is een gap tussen opeenvolgende dits en/of dashes (ddgap)
# een stilte langer dan 2 maal chgap is het begin van een nieuw woord (woordgap)

#__________________________________________________________________________________
#

# Dit gedeete registreert de key-up en key-down bewegingen van de morse seinsleutel.
# Vastgelegd wordt de sleutel beweging: key-down is 0 en key-up is 1 alsmede het
# tijdstip waarop de beweging plaatsvindt.
# Vastlegging in de vorm van getallen paren (key-up/key-down,tijd) die via een
# append aan de lijst buffer worden toegevoegd.

lstint=time.time() # initieer tijdstip  laatste geaccepteerde interrupt

actint=time.time() # initieer tijdstip actuele interrupt

buffer = [0,-2.0,1,-1.0]

# Extra gebruikt voor het testen van dit programma:
# buffer bevat om te beginnen de geseinde tekst "morse trainer" uitgaande van
# een seinsnelheid van 10 woorden per minuut (wpm):
# dit-waarde is 0.139, dash is 3 maal dit, ddgap is dit, lettergap is 3 maal dit,
# woordgap is 7 maal dit

# Zet de begintekst op basis van 10 wpm seinsnelheid, in de buffer
patroon=(0,3,1,3,3,3,1,3,1,3,3,1,1,3,1,1,3,1,1,1,1,1,3,1,7,3,3,1,1,3,1,1,3,1,1,3,
         3,1,1,1,3,3,1,1,3,1,3,1,1,3,1,1)
keytime = 0
for fac in patroon:
    keytime=keytime+fac*0.139
    buffer.append(0)
    buffer.append(keytime)
    
  
# Seinsleutel wordt aangesloten op pin-4 en een aarde-pin van de Raspberry

BUTTON_GPIO = 4

# Interrupt routine die:
# - de beep regelt en
# - de tijdstippen van een seinsleutel-beweging in de buffer vastlegt

key=1

def button_callback(channel):

    global lstint
    global actint
    global key
    
    actint=time.time()
    if actint - lstint > 0.05:  # bounce time 50 msec;
                                # alle interrupts die binnen deze tijd vallen
                                # worden genegeerd
        lstint=actint
        if key==1:
            tone_obj.play(-1)
            key=0
        else:
            tone_obj.stop()
            key=1
        buffer.append(key)
        buffer.append(lstint)


GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH,
callback=button_callback)


#_____________________________________________________________________________
# Omzetten van morse code naar leesbare tekens en op scherm zichtbaar maken

# Vertaal-"tabel": morse code naar leesbare tekens

morse_code_lookup = (
    ("e","t"),
    ("i","a","n","m"),
    ("s","u","r","w","d","k","g","o"),
    ("h","v","f","","l","","p","j","b","x","c","y","z","q","",""),
    ("5","4","","3","","","","2","","","+","","","","","1","6","=",
     "/","","","","","","7","","","","8","","9","0"),
    ("","","","","","","","","","","","","","","","","","","","","",
     ".","","","","","","","","","","","","","","","","","","","","",
     "","","","","","1","6","=","",",","","","","","","","","","","","","")
                    )
def try_decode(morse_code):

# morse_code is een lijst met nullen en enen die in morse code een teken voorstellen:
# een 0 staat voor DIT , een 1 staat voor DASH. Bijvoorbeeld de lijst (0,1,1) staat
# voor de letter w
        
    rij=len(morse_code)-1
    if 0<=rij<=5:
        pos=0
        blok=2**rij
        dcnt=0
        while rij>dcnt:
            pos=pos+morse_code[dcnt]*blok
            blok=blok/2
            dcnt=dcnt+1
        pos=pos+morse_code[dcnt]
        w_rite(morse_code_lookup[int(rij)][int(pos)])
        
# Schrijf tekst naar de GUI 
 
def w_rite(tekst):
    global text_area
    text_area.insert("end",tekst)
    text_area.update_idletasks()
    
#__________________________________________________________________________________    
# Interpreteer de key bewegingen als vastgelegd in de variabele buffer[]

KUT=0       #key-up time
KDT=0       #key-down time

KUL=0       # key-up lengte (duur)
KDL=0       # key-down lengte (duur)

cnt=int(4)  # teller gebruikt bij het verwerken van bufferinhoud: iedere key-down/key-up
            # wordt vastgelegd met vier gegevens: key-down indicater, tijdstip key-down,
            # key-up indicator, tijdstip key-up

morsecode=[] # morse_code is een lijst met nullen en enen die in morse code
             # een teken voorstellen:
             # een 0 staat voor DIT , een 1 staat voor DASH.
             # Bijvoorbeeld de lijst (0,1,1) staat voor de letter w

# dit dash en ddgap worden gebruikt om de kwaliteit van het seinen zelf
# te kunnen beaoordelen. de waarden worden bepaald tijdens het seinen zelf
# initieel op 10 wpm

dit=0.139
dash=3*dit
ddgap=dit

def didah():
    global KUT
    global KDL
    global KDT
    global buffer
    global morsecode
    global dit
    global dash
    global dot
    global cnt

    
    KUT=buffer[cnt+3]
    KDT=buffer[cnt+1]
    KDL=KUT-KDT
    
    if KDL <= dot:
        morsecode.append(0)
        dit=dit+KDL # actuele dit-lengte
        dit=dit/2   # pas aan op actyele dit-lengte
        
    else:
        morsecode.append(1)
        dash=dash+KDL # actuele dash-lengte
        dash=dash/2   # pas aan op actuele dash-lengte
        
    cnt=cnt+4 # volgende key-down/key-up beweging
    
# Display de actuele sein-kwaliteit (verhouding dit en dash lengte) in de GUI    
def display_seinkwaliteit():
    global dash
    global dit
    if 2.8<dash/dit<3.2:
        seinkwaliteit.configure(bg="green") # goed
    elif 2.7<dash/dit<3.3:
        seinkwaliteit.configure(bg="yellow")# redelijk
    elif 2.5<dash/dit<3.5:
        seinkwaliteit.configure(bg="blue")  # twijfelachtig
    else:
        seinkwaliteit.configure(bg="red")   # slecht

#_________________________________________________________________________________
# Verwerk inhoud buffer: opstarten oefening morse geven

ddprint=False   # indien False: nog de samenvatting van de sein-kwalieteit te geven
                # als er meer dan 3 seconden de seinsleutel niet bediend wordt.

running=True    # indien False: de oefening is gestopt door de gebruiker.

def start_geven():
    global buffer
    global KDT
    global cnt
    global KUL
    global KUT
    global morsecode
    global dot
    global ddgap 
    global dit
    global dash
    global chgap
    global ddprint
    global running
    running=True
    w_rite("Oefening gestart")
    w_rite("\n")
    button_start.config(state="disabled")
    button_stop.config(state="active")
    
    while running==True:
        window.update()
        if len(buffer)-cnt>=4:
            ddprint=False
            KUT=buffer[cnt-1] #KUT van voorafgaande dit/dash
            KDT=buffer[cnt+1]
            KUL=KDT-KUT
            if KUL > 2*chgap:           #begin nieuw woord
                try_decode(morsecode) # decodeer laatste character
                display_seinkwaliteit()
                del morsecode[:]
                w_rite(" ")
                didah()         
            elif KUL > chgap:           #begin nieuw character
                try_decode(morsecode) # decodeer laatste character
                display_seinkwaliteit()
                del morsecode[:]
                didah()
            else:                     # volgend dit/dash
                didah()
                ddgap=ddgap+KUL       # KUL is actuele ddgap
                ddgap=ddgap/2         # pas aan op gemiddelde ddgap lengte
                
        else:
            # indien de stilte langer duurt dan 2 seconden laat dan de
            # actuele dit, dash en ddgap waarden zien
            if ddprint==False: 
                if time.time()-lstint > 2:
                    try_decode(morsecode) # decodeer laatste character
                    del morsecode[:]
                    w_rite("\n")
                    w_rite("dit-lengte: "+ str(round(dit,2))+
                           " dash-lengte: "+str(round(dash,2))+
                           " ddgap-lengte: "+ str(round(ddgap,2)))
                    w_rite("\n")
                    ddprint=True
    w_rite("Oefening gestopt")
    w_rite("\n")

#_______________________________________________________________________________
#
def stop_program():
    global running
    running=False
    button_start.config(state="active")
    button_stop.config(state="disabled")
    
#_______________________________________________________________________________    
# Grafisch interface                                        
window=tk.Tk()
window.title("Oefenprogramma Morse Geven")

window.columnconfigure([1,2,3,4],minsize=20)
window.rowconfigure([0,1,2,3,4,5], minsize=20)

seinkwaliteit=tk.Label(text=" sein kwaliteit ",bg="white")
seinkwaliteit.grid(row=2,column=2,columnspan=2)

button_stop=tk.Button(text="Stop oefening",command=stop_program)
button_stop.grid(row=3,column=2)

button_start=tk.Button(text="Start oefening",command=start_geven)
button_start.grid(row=3,column=3)

text_area=tk.Text(wrap = "word")
text_area.grid(row=4,column=2,columnspan=2)

window.mainloop()