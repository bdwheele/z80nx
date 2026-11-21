import sys
import tty
import termios

class Terminal:
    def __init__(self): 
       # test scaffold
        self.original_terminal = termios.tcgetattr(sys.stdin.fileno())
        self.raw = False

    def raw_mode(self):    
        if not self.raw:
            tty.setraw(sys.stdin.fileno())
            self.raw = True

    def cooked_mode(self):
        if self.raw:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSANOW, self.original_terminal)
            self.raw = False


    