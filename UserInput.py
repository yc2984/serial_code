import os
from tkinter import *
from tkinter import messagebox
from Path_file_names import mode_file


def normal(event):
    global mode
    mode = "NORMAL"
    with open(mode_file,'w') as f:
        f.write(mode)
    print("mode is: ",mode)


def load(event):
    global mode
    mode = "LOAD"
    with open(mode_file,'w') as f:
        f.write(mode)
    print("mode is: ", mode)


def LogVolume():
    os.system('python log_volume.py')


def log_mode():
    with open(mode_file, 'r') as f:
        return f.read()


while True:
    root = Tk()
    thelabel1 = Label(root, text="If you changed the logging mode, please close this window to refresh.")
    thelabel1.pack()
    thelabel = Label(root, text="Current Mode is :  %s" % log_mode())
    thelabel.pack()
    topFrame = Frame(root, width=300, height=200)
    topFrame.pack()
    botFrame = Frame(root, width=300, height=200)
    botFrame.pack(side=BOTTOM)

    button_1 = Button(root, text="NORMAL")
    button_1.bind("<Button-1>", normal)
    button_1.pack(side=LEFT)

    button_2 = Button(root, text="LOAD")
    button_2.bind("<Button-1>", load)
    button_2.pack(side=RIGHT)

    #button_3 = Button(botFrame, text="Start Logging Volumes", command= LogVolume)
    #button_3.pack(side=BOTTOM)

    root.mainloop()