from tkinter import *
root = Tk()


def normal(event):
    global mode
    mode = "Normal"
    with open(r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\serial_code\mode.txt",'w') as f:
        f.write(mode)
    print("mode is: ",mode)


def load(event):
    global mode
    mode = "LOAD"
    with open(r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\serial_code\mode.txt",'w') as f:
        f.write(mode)
    print("mode is: ", mode)

button_1 = Button(root, text= "Normal Mode")
button_1.bind("<Button-1>",normal)
button_1.pack()

button_2 = Button(root, text= "LOAD Mode")
button_2.bind("<Button-1>",load)
button_2.pack()

root.mainloop()

