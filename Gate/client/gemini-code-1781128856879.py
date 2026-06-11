# client.py (Updated with Gate Trigger Functionality)
import time
import requests
from picamera import PiCamera
import pytesseract
from PIL import Image
import os
# gpiozero is the modern standard for Pi GPIO control
from gpiozero import DigitalInputDevice, OutputDevice 

# Configuration
PIR_PIN = 17       # GPIO pin connected to PIR OUT (Pin 11)
RELAY_PIN = 23     # GPIO pin connected to Relay IN (Pin 16)
SERVER_URL = "http://YOUR_SERVER_IP:5000/api/check-arrival"
TEMP_IMAGE = "arrival.jpg"

# Initialize Hardware using gpiozero
motion_sensor = DigitalInputDevice(PIR_PIN)
gate_relay = OutputDevice(RELAY_PIN, active_high=True, initial_value=False)
camera = PiCamera()

def trigger_gate_relay():
    """Simulates a button press to open the gate"""
    print("[Hardware] Activating gate relay...")
    gate_relay.on()       # Close the circuit (Trigger gate motor)
    time.sleep(1.0)       # Hold for 1 second
    gate_relay.off()      # Open the circuit 
    print("[Hardware] Relay released.")

def capture_and_process():
    print("\nMotion detected! Capturing image...")
    camera.start_preview()
    time.sleep(1) # Allow camera to adjust to lighting
    camera.capture(TEMP_IMAGE)
    camera.stop_preview()

    try:
        # Pre-process image to grayscale for better OCR
        img = Image.open(TEMP_IMAGE).convert('L')

        # Apply OCR
        text = pytesseract.image_to_string(img, config='--psm 8')
        license_plate = "".join(text.split()).upper()
        
        if len(license_plate) > 3:
            print(f"OCR Result: {license_plate}")
            send_to_server(license_plate)
        else:
            print("OCR did not find a clear license plate.")

    except Exception as e:
        print(f"Error during image processing: {e}")
    finally:
        if os.path.exists(TEMP_IMAGE):
            os.remove(TEMP_IMAGE)

def send_to_server(plate_number):
    payload = {'license_plate': plate_number}
    try:
        response = requests.post(SERVER_URL, json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            
            if result['registered']:
                print("\n" + "="*40)
                print("   ACCESS GRANTED - OPENING GATE")
                print("="*40)
                print(f"Resident:     {result['owner_name']}")
                print(f"Apartment:    {result['apartment_number']}")
                print(f"Parking Bay:  {result['allotted_parking_slot']}")
                print("="*40 + "\n")
                
                # --- PHYSICAL COMMAND TO OPEN THE GATE ---
                trigger_gate_relay()
                
            else:
                print(f"\n[ACCESS DENIED]: Plate {plate_number} not recognized.")
        else:
            print(f"Server Error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection Error: {e}")

print("System Active. Waiting for car arrival...")

# Main Loop
try:
    while True:
        # gpiozero uses .is_active to check the high/low state of the sensor
        if motion_sensor.is_active:
            capture_and_process()
            # 15-second cooldown to let the car pull through before sensing again
            time.sleep(15) 
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nShutting down ALPR system.")