#https://stackoverflow.com/questions/19508353/python-wait-for-user-input-and-if-no-input-after-10-minutes-continue-with-pro
import msvcrt
import time

while True:
    t0 = time.time()
    while time.time() - t0 < 2:
        if msvcrt.kbhit():
            if msvcrt.getch() == '\r\n': # not '\n'
                print("break the program")
                break
        break
        time.sleep(0.1)