from microbit import*
import radio
MORSE_CODE_LOOKUP={".-":"A","-...":"B","-.-.":"C","-..":"D",".":"E","..-.":"F","--.":"G","....":"H","..":"I",".---":"J","-.-":"K",".-..":"L","--":"M","-.":"N","---":"O",".--.":"P","--.-":"Q",".-.":"R","...":"S","-":"T","..-":"U","...-":"V",".--":"W","-..-":"X","-.--":"Y","--..":"Z",".----":"1","..---":"2","...--":"3","....-":"4",".....":"5","-....":"6","--...":"7","---..":"8","----.":"9","-----":"0",".-.-":"_",}
DOT=Image("00000:" "00000:" "00900:" "00000:" "00000:")
DASH=Image("00000:" "00000:" "09990:" "00000:" "00000:")
EMPTY=Image("00000:" "00000:" "00000:" "00000:" "00000:")
ERROR=Image("90009:" "09090:" "00900:" "09090:" "90009:")
RECEIVED_MESSAGES=[]
MESSAGE_ID=0
def handle_receiving():
 incoming=radio.receive()
 if incoming is not None and incoming not in RECEIVED_MESSAGES:
  RECEIVED_MESSAGES.append(incoming)
  relay_string(incoming)
  if get_serial_number()!=incoming.split(":")[1]:
   display_string(incoming.split(":")[2])
  else:
   RECEIVED_MESSAGES.append(incoming)
def send_string(message):
 global MESSAGE_ID
 radio.send(str(MESSAGE_ID)+":"+get_serial_number()+":"+message)
 MESSAGE_ID=MESSAGE_ID+1
def relay_string(message):
 radio.send(message)
def display_string(message):
 display.scroll(message)
def display_dot():
 display.show(DOT)
 sleep(300)
 display.show(EMPTY)
def display_dash():
 display.show(DASH)
 sleep(300)
 display.show(EMPTY)
def display_cancelled():
 display.show(ERROR)
 sleep(1000)
 display.show(EMPTY)
def display_error():
 display.show(Image.SAD)
 sleep(1000)
 display.show(EMPTY)
def display_char(char):
 display.show(char)
 sleep(300)
 display.show(EMPTY)
def display_sending_arrow():
 display.show(Image.ARROW_N)
 sleep(1000)
 display.show(EMPTY)
def get_serial_number(type=hex):
 NRF_FICR_BASE=0x10000000
 DEVICEID_INDEX=25 
 @micropython.asm_thumb
 def reg_read(r0):
  ldr(r0,[r0,0])
 return type(reg_read(NRF_FICR_BASE+(DEVICEID_INDEX*4)))
def get_character_from_morse(morse_character):
 global MORSE_CODE_LOOKUP
 if morse_character is None:
  return None
 elif len(morse_character)>5:
  return None
 elif morse_character in MORSE_CODE_LOOKUP.keys():
  return MORSE_CODE_LOOKUP.get(morse_character)
 else:
  return None
def is_display_busy():
 for x in range(5):
  for y in range(5):
   if display.get_pixel(x,y)>0:
    return True
 return False
def get_morse_character():
 morse_character=''
 time_since_last_input=0
 while(len(morse_character)<=5)and(time_since_last_input<1000):
  if button_a.is_pressed()and button_b.is_pressed():
   return None
  elif button_a.is_pressed():
   morse_character+='.'
   display_dot()
   time_since_last_input=0
  elif button_b.is_pressed():
   morse_character+='-'
   display_dash()
   time_since_last_input=0
  sleep(10)
  time_since_last_input+=10
 return morse_character
def handle_sending():
 message=""
 if button_a.is_pressed()or button_b.is_pressed():
  while True:
   if accelerometer.was_gesture('shake'):
    display_cancelled()
    return
   if not is_display_busy():
    display.scroll(message,wait=False)
   if button_a.is_pressed()or button_b.is_pressed():
    morse_character=get_morse_character()
    char=get_character_from_morse(morse_character)
    if morse_character is not None:
     if char is not None:
      display_char(char)
      message+=char
     else:
      display_error()
   current_send_button_hold_time=0
   while button_a.is_pressed()and button_b.is_pressed():
    sleep(10)
    current_send_button_hold_time+=10
    if current_send_button_hold_time>=1000:
     send_string(message)
     display_sending_arrow()
     sleep(1000)
     return
def main():
 radio.on()
 radio.config(address=453087619471048165876140186748)
 while True:
  handle_sending()
  handle_receiving()
 radio.off()
main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
