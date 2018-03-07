import threading
import time
from pad4pi import rpi_gpio
import requests
import json

#Setup Keypad
KEYPAD = [
   [1, 2, 3, "A"],
   [4, 5, 6, "B"],
   [7, 8, 9, "C"],
   ["*", 0, "#", "D"]
]

COL_PINS = [18, 27, 22, 23]  #BCM Pin Numbering
ROW_PINS = [4, 14, 15, 17] #Also BCM Pin Numbering

global barcode
barcode = []

global lastKey
lastKey = ""

def printKey(key):
    global barcode
    global lastKey
    lastKey = str(key)
    #print(key)
    barcode.append(key)

def runJob():
    global barcode
    global lastKey
    global dead1
    try:
        factory = rpi_gpio.KeypadFactory()
        keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)
        #printKey will be called each time a keypad button is pressed
        keypad.registerKeyPressHandler(printKey)
   
        
       #print("Press buttons on your keypad. Ctrl+C to exit.")
        while (not dead1):
            global lastKey
            if ( lastKey == "#"):
                payload = json.dumps(barcode)
                #print(payload)
                
                barcodeString = payload
                b = "[],#\" "
                for char in b:
                    barcodeString = barcodeString.replace(char,"")
                print (barcodeString)
                siteString = "http://18.219.186.47:5000/receiveBarcode/%s" %barcodeString
                #print(siteString)
                r = requests.post(siteString, json=payload)
               # print(r.text)
                #print(barcode)
                barcode = []
                lastKey = ""
            time.sleep(1)
            
    except KeyboardInterrupt:
        #print(barcode)
   
        print("Goodbye")
    finally:
        keypad.cleanup()   

global dead1
dead1 = False
thread1 = threading.Thread(target=runJob)
thread1.start();