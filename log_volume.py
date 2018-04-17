import sys
import os
import time
import datetime
import pandas as pd
from Lookup_tank_name import id_to_tankname, tanklist, table

reading_plus_file = r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\GLM_maker_test\03042018\AUDAX - GHS_Version16\AUDAX\READINGS+.TXT"
logpath = r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\Log"


def log_mode(default="Normal"):
    """ This function read from user input. By default, normal mode is selected."""
    log_mode = input("Please enter LOAD to enter loading mode:")
    return log_mode


# The normal mode
def read_volume(df_vols, vol_file, time_to_average_on, sample_rate):
    """
    1. Read READING+.txt file for real-time volumes
    2. refresh the df_vols that has all the tank reading in the last defined time_gap
    3. returns
        (1) current volumes, list
        (2) average reading from the last time_gap, list
        (3) all the tank names, list
    """
    df_current_vol = pd.read_csv(vol_file, header=None)
    current_vol_list = df_current_vol.iloc[:, 1].tolist()
    num_rows = time_to_average_on / (60 / sample_rate)  # eg. sample_rate 12, means read every 5 seconds
    if len(df_vols) < num_rows:
        df_vols = pd.concat([df_vols, pd.DataFrame(current_vol_list).T], axis=0)
    else:
        df_vols = pd.concat([df_vols.tail(num_rows-1), pd.DataFrame(current_vol_list).T], axis=0)

    average_vol = df_vols.mean(numeric_only=True, axis=0).tolist()
    assert isinstance(average_vol, list)
    return current_vol_list, average_vol, len(df_vols)


def volume_change(average_vol, current_vol, threshold):
    """ This function compares two list, return True if
    at least one of the tank volume changed more than 50 tons """
    if max([abs(a-b) for a,b in zip(current_vol,average_vol)]) >= threshold:
        return True
    else:
        return False


def write_file(data, logpath, filename, header, if_header, write_mode):
    """
    Write or append new record to a csv file.
    Note: Data should be a list, including timestamp as the first element
    """
    with open(os.path.join(logpath, filename), write_mode) as f:
        df = pd.DataFrame(data).T
        df.columns = header
        df.to_csv(f, index=None, header=if_header)


def main(logpath, log_mode, sample_rate):
    """This function logs the volume to a csv file when:
    compared with last minute average
    at least one of the tank volume changed more than 50 tons
    """
    df_vols = pd.DataFrame()
    start_time = time.time()
    while True:
        tanknames = tanklist(reading_plus_file)
        vol_daily_file = str(datetime.datetime.now().strftime("%Y-%m-%d")) + str("_vol_m3.csv")
        time.sleep(60/sample_rate)
        current_vol_list = read_volume(df_vols, reading_plus_file, 60, 12)[0]
        average_vol_list = read_volume(df_vols, reading_plus_file, 60, 12)[1]
        len_df_vols = read_volume(df_vols, reading_plus_file, 60, 12)[2]

        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_vol_list = [current_date_time] + current_vol_list
        print("length of current_data_list",len(current_vol_list))
        print("length of the data to log:", len(current_time_vol_list))
        log_header = ["Time"] + tanknames
        print("length of the header",len(log_header))
        if len_df_vols == 1:
            write_file(current_time_vol_list, logpath, vol_daily_file, log_header, True, 'w+')
            continue
        if volume_change(average_vol_list, current_vol_list, 50):
            write_file(current_time_vol_list, logpath, vol_daily_file, log_header, False, 'a')
            df_vols = pd.concat([df_vols, pd.DataFrame(current_vol_list).T], axis=0)
            print("new value has been logged")


if __name__ == "__main__":
    main(logpath, log_mode(default="Normal"), 12)


