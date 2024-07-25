import firebase_admin
from firebase_admin import credentials, db
import threading
import time
import curses
from colorama import Fore, Style
import os
import signal
import sys

# Firebase configuration
cred = credentials.Certificate('/root/tools/Anon-Chat/firebase.json')  # Path to the downloaded JSON file
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://zusy-b8921-default-rtdb.firebaseio.com/'
})

messages = []

def signal_handler(sig, frame):
    print(Fore.LIGHTRED_EX + Style.BRIGHT + "[EXITING]" + Fore.LIGHTWHITE_EX + " Goodbye!" + Fore.WHITE + Style.RESET_ALL)
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

def send_message(username, stdscr):
    curses.curs_set(1)  # Make cursor visible
    input_line = curses.LINES - 1  # Input line position
    stdscr.clear()
    stdscr.refresh()

    while True:
        stdscr.addstr(input_line, 0, f'{username}: ')
        stdscr.clrtoeol()  # Clear the screen and place cursor at the input line
        stdscr.refresh()

        message = ""
        stdscr.addstr(input_line, len(username) + 2, message)
        stdscr.move(input_line, len(username) + 2)
        
        while True:
            key = stdscr.getch()
            if key in [curses.KEY_ENTER, 10, 13]:  # Enter key
                break
            elif key in [curses.KEY_BACKSPACE, 127]:  # Backspace key
                if len(message) > 0:
                    message = message[:-1]  # Remove last character
                    stdscr.addstr(input_line, len(username) + 2, ' ' * (curses.COLS - len(username) - 2))  # Clear the line
                    stdscr.addstr(input_line, len(username) + 2, message)  # Write updated message
                    stdscr.move(input_line, len(username) + 2 + len(message))  # Move cursor to the correct position
            elif 32 <= key <= 126 and len(message) < curses.COLS - len(username) - 3:  # Normal printable characters and within terminal width
                message += chr(key)
                stdscr.addstr(input_line, len(username) + 2, message)  # Write the message
                stdscr.move(input_line, len(username) + 2 + len(message))  # Move cursor to the correct position
            stdscr.refresh()

        if message:
            db.reference('messages').push({
                'username': username,
                'message': message,
                'timestamp': time.time()
            })
        stdscr.addstr(input_line, 0, ' ' * (curses.COLS - 1))  # Clear the line
        stdscr.refresh()

def listen_for_messages(stdscr, username):
    def listener(event):
        data = event.data
        if data and isinstance(data, dict) and 'username' in data and 'message' in data:
            messages.append(f"{data['username']}: {data['message']}")
            stdscr.clear()  # Clear the screen
            # Write "DarkWeb" at the top
            stdscr.addstr(0, 0, 'Welcome to DarkWeb', curses.A_BOLD | curses.color_pair(1))
            # Write messages from top to bottom with 3 lines of padding
            start_line = 2
            for idx, msg in enumerate(messages[-(curses.LINES - start_line):]):
                stdscr.addstr(start_line + idx, 0, msg)
            # Rewrite the input line
            input_line = curses.LINES - 1
            stdscr.addstr(input_line, 0, f'{username}: ')
            stdscr.refresh()

    messages_ref = db.reference('messages')
    messages_ref.listen(listener)

def main(stdscr, username):
    curses.curs_set(0)  # Hide cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    stdscr.clear()
    stdscr.refresh()

    # Print "DarkWeb" at the top
    stdscr.addstr(0, 0, 'Welcome to DarkWeb', curses.A_BOLD | curses.color_pair(1))
    
    listener_thread = threading.Thread(target=listen_for_messages, args=(stdscr, username))
    listener_thread.daemon = True
    listener_thread.start()

    send_message(username, stdscr)

if __name__ == "__main__":
    logo = """
    
8888888b.                   888           888       888          888      
888  "Y88b                  888           888   o   888          888      
888    888                  888           888  d8b  888          888      
888    888  8888b.  888d888 888  888      888 d888b 888  .d88b.  88888b.  
888    888     "88b 888P"   888 .88P      888d88888b888 d8P  Y8b 888 "88b 
888    888 .d888888 888     888888K       88888P Y88888 88888888 888  888 
888  .d88P 888  888 888     888 "88b      8888P   Y8888 Y8b.     888 d88P 
8888888P"  "Y888888 888     888  888      888P     Y888  "Y8888  88888P"  
    """
    time.sleep(1)
    os.system('clear')
    time.sleep(1)
    print(Fore.LIGHTBLACK_EX + logo + Fore.WHITE)
    print("                	                         		    By Zusy " + Fore.LIGHTRED_EX + Style.BRIGHT + "<3" + Style.RESET_ALL + Fore.WHITE + "")
    time.sleep(1)

    while True:
        username = input("Username : ").strip()
        if username:
            break
        else:
            time.sleep(1)
            print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "\n[MESSAGE]" + Fore.LIGHTRED_EX + " Login Failed. Please enter a valid name.\n" + Fore.WHITE + Style.RESET_ALL)
            time.sleep(1)
    
    print("")
    time.sleep(1)
    print(Fore.LIGHTBLUE_EX + Style.BRIGHT + "[MESSAGE]" + Fore.LIGHTGREEN_EX + " Login successful!" + Fore.WHITE + Style.RESET_ALL)
    time.sleep(2)
    print("")
    curses.wrapper(main, username)
