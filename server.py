import socket
import time
import random
from gpiozero import LED


leds = [LED(27), LED(26), LED(17), LED(16), LED(19)]
current_game = 0
animation_step = 0


def turn_off_all_leds():
   for led in leds:
       led.off()


def run_game_step():
   global animation_step
   if current_game == 0:
       return
  
   turn_off_all_leds()
  
   if current_game == 33:    # Chaser
       leds[animation_step % len(leds)].on()
       animation_step += 1
      
   elif current_game == 34:  # Bounce
       sequence = [0, 1, 2, 3, 4, 3, 2, 1]
       leds[sequence[animation_step % len(sequence)]].on()
       animation_step += 1
      
   elif current_game == 35:  # Alternating
       if animation_step % 2 == 0:
           leds[0].on(); leds[4].on()
       else:
           leds[1].on(); leds[2].on(), leds[3].on()
       animation_step += 1
      
   elif current_game == 36:  # Heartbeat
       if (animation_step % 4) in [0, 2]:
           for led in leds: led.on()
       animation_step += 1
      
   elif current_game == 37:  # Neon
       for led in leds:
           if random.choice([True, False]):
               led.on()


def start_server():
   global current_game, animation_step
   with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
       s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       s.bind(('0.0.0.0', 65432))
       s.listen()
       s.settimeout(0.05)
       print("Server listening...")
      
       try:
           while True:
               try:
                   conn, addr = s.accept()
                   with conn:
                       data = conn.recv(1)
                       if data:
                           val = data[0]
                           if val > 32:
                               current_game = val
                               animation_step = 0
                           else:
                               current_game = 0
                               turn_off_all_leds()
                               for i in range(len(leds)):
                                   if val & (1 << i):
                                       leds[i].on()
               except socket.timeout:
                   run_game_step()
                   time.sleep(0.1)
       except KeyboardInterrupt:
           print("\nShutting down server...")
           turn_off_all_leds()


if __name__ == "__main__":
   start_server()



