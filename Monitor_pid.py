import os
import tkinter
from Path_file_names import readonly_path, mode_file
import psutil


def status(message, title, log_mode, width=200, height=40, color="Black"):
    root = tkinter.Tk()
    root.title(title)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    thelabel1 = tkinter.Label(root, text=message, fg=color)
    thelabel1.pack()
    thelabel2 = tkinter.Label(root, text=log_mode, fg=color)
    thelabel2.pack()
    root.attributes("-topmost", True)
    root.after(2000, lambda: root.destroy())

    # calculate position x and y coordinates
    x = screen_width - width
    y = screen_height - 4*height
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    root.mainloop()


def check_status(pid_file, processname):
    with open(mode_file, 'r') as f:
        log_mode = f.read()
    try:
        file = open(os.path.join(readonly_path, pid_file),'r')
        pid = int(file.read())
        file.close()

        if psutil.pid_exists(pid):
            print("%s is running" % processname)
            status("%s is running" % processname, "STATUS", "logging mode: "+log_mode)
        else:
            print("%s is NOT running" % processname)
            status("%s is NOT running" % processname, "WARNING", "logging mode: "+log_mode, color='red')
    except OSError:
        print("%s is NOT started" % processname)
        status("%s is NOT started" % processname, "WARNING", "logging mode: "+log_mode, color='red')


while True:
    check_status("pid_modbus-tk-test.txt", "Read Modbus")
    check_status("pid_log_volume.txt","Log volume")
    check_status("pid_trimheel.txt","Read Trim Heel")




