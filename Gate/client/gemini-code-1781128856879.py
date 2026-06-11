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