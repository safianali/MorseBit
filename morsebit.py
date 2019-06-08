# Import dependencies
from microbit import *
import radio

###############################
### GLOBAL CONFIG CONSTANTS ###
###############################
MORSE_CODE_LOOKUP = {
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    "-----": "0",
    ".-.-": "_",
}
DOT = Image("00000:"
            "00000:"
            "00900:"
            "00000:"
            "00000:")
DASH = Image("00000:"
             "00000:"
             "09990:"
             "00000:"
             "00000:")
EMPTY = Image("00000:"
              "00000:"
              "00000:"
              "00000:"
              "00000:")
ERROR = Image("90009:"
              "09090:"
              "00900:"
              "09090:"
              "90009:")


###############################
### GLOBAL CONFIG VARIABLES ###
###############################
RECEIVED_MESSAGES = []
MESSAGE_ID = 0


###################
### SUBROUTINES ###
###################
# Handles receiving incoming communications
def handle_receiving():
    # Receive most recent queued radio signals
    incoming = radio.receive()
    if incoming is not None and incoming not in RECEIVED_MESSAGES:
        # Add the received message so it isn't re-displayed.
        RECEIVED_MESSAGES.append(incoming)
        relay_string(incoming)

        # Don't display message if it originated from the same device
        if get_serial_number() != incoming.split(":")[1]:
            display_string(incoming.split(":")[2])
        else:
            RECEIVED_MESSAGES.append(incoming)


# Sends a encoded string on the radio channel.
def send_string(message):
    # Send the message, incrementing the message ID in the process.
    global MESSAGE_ID
    radio.send(str(MESSAGE_ID) + ":" + get_serial_number() + ":" + message)
    MESSAGE_ID = MESSAGE_ID + 1


# Relays an incoming radio signal to extend potential range.
def relay_string(message):
    # Send the message
    radio.send(message)


# Handles displaying a string on the morse:bit display
def display_string(message):
    display.scroll(message)


# Prints a '.' morse code on the display
def display_dot():
    display.show(DOT)
    sleep(300)
    display.show(EMPTY)


# Prints a '-' morse code on the display
def display_dash():
    display.show(DASH)
    sleep(300)
    display.show(EMPTY)


# Displays an 'x' on the display
def display_cancelled():
    display.show(ERROR)
    sleep(1000)
    display.show(EMPTY)


# Displays an error on the display
def display_error():
    display.show(Image.SAD)
    sleep(1000)
    display.show(EMPTY)


# Display a character on the display
def display_char(char):
    display.show(char)
    sleep(300)
    display.show(EMPTY)


# Prints a sent arrow on the display
def display_sending_arrow():
    display.show(Image.ARROW_N)
    sleep(1000)
    display.show(EMPTY)


# Gets the unique serial number of a micro:bit device from the FICR
def get_serial_number(type=hex):
    NRF_FICR_BASE = 0x10000000
    DEVICEID_INDEX = 25 # deviceid[1]

    @micropython.asm_thumb
    def reg_read(r0):
        ldr(r0, [r0, 0])
    return type(reg_read(NRF_FICR_BASE + (DEVICEID_INDEX*4)))


# Gets a specific character from the morse code lookup dictionary.
def get_character_from_morse(morse_character):
    global MORSE_CODE_LOOKUP
    if morse_character is None:
        return None
    elif len(morse_character) > 5:
        return None
    elif morse_character in MORSE_CODE_LOOKUP.keys():
        return MORSE_CODE_LOOKUP.get(morse_character)
    else:
        return None


# Checks if the display is currently busy by checking if any pixels on it are active.
def is_display_busy():
    for x in range(5):
        for y in range(5):
            if display.get_pixel(x,y) > 0:
                return True
    return False


# Gets a character in morse code from the input
def get_morse_character():
    morse_character = ''
    time_since_last_input = 0

    while (len(morse_character) <= 5) and (time_since_last_input < 1000):
        if button_a.is_pressed() and button_b.is_pressed():
            return None
        elif button_a.is_pressed():
            morse_character += '.'
            display_dot()
            time_since_last_input = 0
        elif button_b.is_pressed():
            morse_character += '-'
            display_dash()
            time_since_last_input = 0

        sleep(10)
        time_since_last_input += 10

    return morse_character


# Handle the build up and sending of messages
def handle_sending():
    # The currently constructed morse code message and related variables.
    message = ""

    if button_a.is_pressed() or button_b.is_pressed():
        # Continue checking for input until the user has sent their message. This is essentially a send state.
        while True:
            if accelerometer.was_gesture('shake'):
                display_cancelled()
                return
            if not is_display_busy():
                display.scroll(message, wait=False)
            if button_a.is_pressed() or button_b.is_pressed():
                morse_character = get_morse_character()
                char = get_character_from_morse(morse_character)
                if morse_character is not None:
                    if char is not None:
                        display_char(char)
                        message += char
                    else:
                        display_error()

            # Check if both buttons are being held, if they are then track them. If held for long enough send the
            # message.
            current_send_button_hold_time = 0
            while button_a.is_pressed() and button_b.is_pressed():
                sleep(10)
                current_send_button_hold_time += 10

                if current_send_button_hold_time >= 1000:
                    send_string(message)
                    display_sending_arrow()
                    sleep(1000)
                    return


############
### MAIN ###
############
def main():
    # Turn the radio on and tune into the morse:bit channel
    radio.on()
    radio.config(address=453087619471048165876140186748)
    while True:
        handle_sending()
        # Wait before checking received strings.
        handle_receiving()

    radio.off()


main()