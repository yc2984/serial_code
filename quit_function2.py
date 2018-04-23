#https://stackoverflow.com/questions/19508353/python-wait-for-user-input-and-if-no-input-after-10-minutes-continue-with-pro
import msvcrt
import time
def ReadUserInput():
    t0 = time.time()
    while True:
        if time.time() - t0 < 2:
            if msvcrt.kbhit():
                if msvcrt.getch() == '\r\n': #
                    print("break the program")
                    return 1
            elif time.time() - t0 > 2:
                continue