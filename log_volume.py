import math
import os
import time
import datetime
import pandas as pd
from Lookup_tank_name import id_to_tankname, tanklist, table

reading_plus_file = r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\GLM_maker_test\03042018\AUDAX - GHS_Version16\AUDAX\READINGS+.TXT"
logpath = r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\Log"


def log_mode():
    """ This function read from user input. By default, normal mode is selected."""
    log_mode = input("Please enter LOAD to enter loading mode:")
    if log_mode == "":
        return "Normal"
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
    if len(df_vols) == 1 or len(df_vols) < num_rows*2:
        print("%d values will be used for average" % num_rows)
        print("Before adding new record, the df_vols has %d records" % len(df_vols))
        df_vols = pd.concat([df_vols, pd.DataFrame(current_vol_list).T], axis=0)
        print("After adding new record, the df_vols has %d records" % len(df_vols))
    else:
        print("Before adding new record, the df_vols has %d records" % len(df_vols))
        df_vols = pd.concat([df_vols.tail(int(num_rows-1)), pd.DataFrame(current_vol_list).T], axis=0)
        print("After adding new record, the df_vols has %d records" % len(df_vols))

    average_vol1 = df_vols[:len(df_vols)/2, :].mean(numeric_only=True, axis=0).tolist()
    average_vol2 = df_vols[len(df_vols)/2:, :].mean(numeric_only=True, axis=0).tolist()
    assert isinstance(average_vol1, list)
    assert isinstance(average_vol2, list)
    return current_vol_list, average_vol1, average_vol2, len(df_vols), df_vols


def volume_change(vol1, vol2, threshold):
    """ This function compares two list, return True if
    at least one of the tank volume changed more than 50 tons """
    if max([abs(a-b) for a, b in zip(vol1, vol2)]) >= threshold:
        print("at least one volume has changed more than %d" % threshold)
        print([abs(a-b) for a, b in zip(vol1, vol2)][:5])
        return True
    else:
        print("no volume has changed more than %d" % threshold)
        print([abs(a - b) for a, b in zip(vol1, vol2)][:5])
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
        time.sleep(60 / sample_rate)
        print("It's %s mode" %log_mode)
        tanknames = tanklist(reading_plus_file)
        vol_daily_file = str(datetime.datetime.now().strftime("%Y-%m-%d")) + str("_vol_m3.csv")
        current_vol_list, average_vol_list1, average_vol_list2, len_df_vols, df_vols = read_volume(df_vols, reading_plus_file, 60, sample_rate)

        print("Now the live data for average has %d items" % len_df_vols)

        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_vol_list = [current_date_time] + current_vol_list
        print("length of current_data_list", len(current_vol_list))
        print("length of the data to log:", len(current_time_vol_list))
        log_header = ["Time"] + tanknames
        print("length of the header",len(log_header))
        if len_df_vols == 1:
            write_file(current_time_vol_list, logpath, vol_daily_file, log_header, True, 'w+')
            print("You have logged the first value")
            continue
        if volume_change(average_vol_list1, average_vol_list2, 50) or log_mode == "LOAD":
            write_file(current_time_vol_list, logpath, vol_daily_file, log_header, False, 'a')
            print("new value has been logged")


if __name__ == "__main__":
    main(logpath, log_mode(), 30)


