import socket 

RPI_IP = '192.168.5.69'
PORT = 65432

def send_bytes(value):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((RPI_IP, PORT))
            s.sendall(bytes([value & 0xFF]))
            print (f"Byte {value} inviato con successo")
    except Exception as e:
        print (f"Errore: {e}")

print ("--- Termianle Invio Byte ---")
print("Inserisci un numero tra 0 e 255")

while True:
    user_input = input("\nValore da inviare:")

    if user_input.lower() == "q":
        break

    if user_input.isdigit():
        val = int(user_input)
        if 0 <= val <= 255:
            send_bytes(val)
        else:
            print("Inserisci un numero valido (0-255)")
    else:
        print("Inserisci solo numeri")