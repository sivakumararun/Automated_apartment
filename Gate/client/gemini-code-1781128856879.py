# client.py - Running on Raspberry Pi
import time
import requests
import Adafruit_GPIO.GPIO as GPIO
from picamera import PiCamera
import pytesseract
from PIL import Image
import os

# Configuration
PIR_PIN = 17  # GPIO pin connected to PIR OUT
SERVER_URL = "http://YOUR_SERVER_IP:5000/api/check-arrival"
TEMP_IMAGE = "arrival.jpg"

# Tesseract setup (ensure tesseract-ocr is installed on Pi)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
camera = PiCamera()

def capture_and_process():
    print("Motion detected! Capturing image...")
    
    # Warm up camera, set focus if necessary
    camera.start_preview()
    time.sleep(1) # Important for lighting adjustment
    camera.capture(TEMP_IMAGE)
    camera.stop_preview()

    try:
        # Pre-process image (grayscale improves OCR accuracy)
        img = Image.open(TEMP_IMAGE).convert('L')
        # (Optional: Add more processing like thresholding)

        # Apply OCR
        # config='--psm 8' tells Tesseract to look for a single word/block
        text = pytesseract.image_to_string(img, config='--psm 8')
        license_plate = "".join(text.split()).upper() # Clean the text
        
        if len(license_plate) > 3: # Ignore trivial OCR noise
            print(f"OCR Result: {license_plate}")
            send_to_server(license_plate)
        else:
            print("OCR did not find a valid plate.")

    except Exception as e:
        print(f"Error during processing: {e}")
    finally:
        os.remove(TEMP_IMAGE) # Clean up

# Update the send_to_server function in your client.py file:

def send_to_server(plate_number):
    payload = {'license_plate': plate_number}
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            if result['registered']:
                print("\n" + "="*40)
                print("   ACCESS GRANTED - GATE OPENING")
                print("="*40)
                print(f"Resident:     {result['owner_name']}")
                print(f"Apartment:    {result['apartment_number']}")
                print(f"Parking Bay:  {result['allotted_parking_slot']}")
                print("="*40 + "\n")
                
                # physical_gate_relay_trigger()
            else:
                print(f"ACCESS DENIED: Plate {plate_number} not recognized.")
        else:
            print(f"Server Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")

print("System Active. Waiting for car arrival...")

# Main Loop
try:
    while True:
        if GPIO.input(PIR_PIN):
            capture_and_process()
            # Cool down to prevent multiple triggers from one car
            time.sleep(10)
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()