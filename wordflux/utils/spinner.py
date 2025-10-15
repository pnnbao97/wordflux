import sys
import time
import threading

class Spinner:
    def __init__(self, message="Processing"):
        self.spinner_chars = ['|', '/', '-', '\\']
        self.message = message
        self.spinning = False
        self.thread = None
    
    def spin(self):
        i = 0
        while self.spinning:
            sys.stdout.write(f'\r{self.message}... {self.spinner_chars[i % len(self.spinner_chars)]}')
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()
    
    def start(self):
        self.spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
    
    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join()