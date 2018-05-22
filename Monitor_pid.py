import os
import tkinter
from Path_file_names import readonly_path
import psutil


def status(message, title, width=200, height=30, color="Black"):
    root = tkinter.Tk()
    root.title(title)
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    thelabel1 = tkinter.Label(root, text=message, fg=color)
    thelabel1.pack()
    root.attributes("-topmost", True)
    root.after(2000, lambda: root.destroy())

    # calculate position x and y coordinates
    x = screen_width - width
    y = screen_height - 4*height
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))
    root.mainloop()


def check_status(pid_file, processname):
    try:
        file = open(os.path.join(readonly_path, pid_file),'r')
        pid = int(file.read())
        file.close()

        if psutil.pid_exists(pid):
            print("%s is running" % processname)
            status("%s is running" % processname,"STATUS")
        else:
            print("%s is NOT running" % processname)
            status("%s is NOT running" % processname, "WARNING", color='red')
    except OSError:
        print("%s is NOT started" % processname)
        status("%s is NOT started" % processname, "WARNING", color='red')


while True:
    check_status("pid_modbus-tk-test.txt", "Read from Modbus")
    check_status("pid_log_volume.txt","Log volume")
    check_status("pid_trimheel.txt","Read Trim Heel")




