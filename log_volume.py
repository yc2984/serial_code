import os
import time
import datetime
import pandas as pd
from Lookup_tank_name import id_to_tankname
from pathlib import Path
from Path_file_names import logpath, reading_plus_file, mode_file, sample_rate, sample_period, readonly_path
import tkinter
from tkinter import messagebox


def warning(message):
    print("Please first start GLM")
    root = tkinter.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showwarning("Warning", message)


def read_volume(vol_file):
    """
    1. Read READING+.txt file for real-time volumes
    2. returns the volume list of the tanks
    """
    try:
        file = open(vol_file)
    except PermissionError: # file is being written by GLM.
        return None, None
    except OSError:
        warning("READINGS+.txt doesn't exist, please start GLM")
        return None, None

    df_current_vol = pd.read_csv(file, header=None)
    file.close()
    print("length of READINGS+.txt (should be 123):", len(df_current_vol))

    # If GLM is not open or Send volume is not on,  READINGS+.txt will be empty
    if len(df_current_vol) < 123:
        warning("Please Start GLM and turn on SEND VOLUME to start logging")
        return None, None
    # Read tank volumes
    current_vol_list = df_current_vol.iloc[:, 1].tolist()
    # Read tank id and convert to names
    ids = df_current_vol.iloc[:, 0]
    tanknames = []
    for id in ids:
        tankname = id_to_tankname(id)
        tanknames.append(tankname)
    return tanknames, current_vol_list


def write_file(data, logpath, filename, header, filename2):
    """
    Write or append new record to a csv file.
    Note: Data should be a list, including timestamp as the first element
    If file exist, append to it, otherwise create new one.)
    """
    my_file = Path(os.path.join(logpath, filename))
    if my_file.is_file():
        if_header = False
        write_mode = 'a'
    else:
        write_mode = 'w+'
        if_header = True
    try:
        with open(my_file, write_mode) as f:
            df = pd.DataFrame(data).T
            df.columns = header
            df.to_csv(f, index=None, header=if_header)
    except PermissionError:
        print("Please CLOSE the log file")
        my_file_2 = Path(os.path.join(logpath, filename2))
        root = tkinter.Tk()
        root.withdraw()
        messagebox.showwarning("Warning", "Please CLOSE the log file %s" %my_file)
        print("The main log file is open, logged in %s" %my_file_2)
        with open(my_file_2, write_mode) as f:
            df = pd.DataFrame(data).T
            df.columns = header
            df.to_csv(f, index=None, header=if_header)


def main(logpath, sample_rate=60, sample_period=60):
    """This function logs the volume to a csv file.
    1. For LOAD mode, log every second
    2. For NORMAL mode, log every minute
    """
    t0 = time.time()
    while True:
        # this defines the frequency of the main loop, in this case every 1 second.
        time.sleep(60 / sample_rate)
        t1 = time.time()
        current_date_time = datetime.datetime.now()
        print("\n")
        print("Start")
        with open(mode_file,'r') as f:
            log_mode = f.read()
        print("It's %s mode" %log_mode)

        # Read the file READINGS+.txt
        tanknames, current_vol_list = read_volume(reading_plus_file)
        if (tanknames or current_vol_list) is None:
            continue

        # filename of the logs
        vol_daily_file = str(current_date_time.strftime("%Y-%m-%d")) + str("_vol_m3.csv")
        filename2 = str(current_date_time.strftime("%Y-%m-%d")) + str("_vol_m3_02.csv")

        # Appending time and log mode
        current_date_time_format = current_date_time.strftime("%Y-%m-%d %H:%M:%S")
        time_mode_vol_list = [current_date_time_format] + [log_mode] + current_vol_list
        print("length of current_data_list (should be 125)", len(time_mode_vol_list))

        log_header = ["Time"] + ["log_mode"] + tanknames
        print("length of the header (should be 125)", len(log_header))
        assert len(log_header) == len(time_mode_vol_list)

        # Create log file
        second = int(t1) - int(t0)
        print("This is %dth second" % second)
        if log_mode == "NORMAL":
            if int(t1) > 1 and second % sample_period == 0:  # log per minute.
                write_file(time_mode_vol_list, logpath, vol_daily_file, log_header, filename2)
                print("Normal Mode, new value has been logged")
                assert isinstance(int(second / sample_period),int)
                print("######## It's the %dth sample_period, volumes are logged" % int(second / sample_period))
                print("The first five volumes logged: ", time_mode_vol_list[:5])
            else:
                print("Nothing logged, only log per %d second" %sample_period)
        else:  # Load mode
            write_file(time_mode_vol_list, logpath, vol_daily_file, log_header, filename2)
            print("LOAD mode, new value has been logged")


a = os.getpid()
with open(os.path.join(readonly_path,"pid_log_volume.txt"),"w") as f:
    f.write(str(a))

if __name__ == "__main__":
    main(logpath, sample_rate, sample_period)  # log_path, sample rate, sample period.


