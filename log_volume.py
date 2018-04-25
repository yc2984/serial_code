import math
import os
import time
import datetime
import pandas as pd
from Lookup_tank_name import id_to_tankname, tanklist, table
from pathlib import Path
from Path_file_names import logpath, reading_plus_file, mode_file


def read_volume(df_vols, vol_file, sample_period, sample_rate):
    """
    1. Read READING+.txt file for real-time volumes
    2. refresh the df_vols that has all the tank reading in the last defined time_gap
    3. returns
        (1) average volume of the second last minute
        (2) average volume of the last minute
        (3) the live table
        (4) the number of rows required to start logging
        (5) the number of rows in current live table

    """
    df_current_vol = pd.read_csv(vol_file, header=None)
    current_vol_list = df_current_vol.iloc[:, 1].tolist()
    num_rows = sample_period/(60/sample_rate) # If sample_rate = 60, sample period 60 seconds, num_rows is 60.
    print("%d values will be used for average" % num_rows)
    print("Before adding new record, the df_vols has %d records" % len(df_vols))

    if len(df_vols) < num_rows*2-1: # skip the first two average period
        df_vols = pd.concat([df_vols, pd.DataFrame(current_vol_list).T], axis=0)
        print("After adding new record, the df_vols has %d records" % len(df_vols))
        return '', '', df_vols, num_rows, len(df_vols)  # The length after append current reading.
    else:
        df_vols = pd.concat([df_vols.tail(int(2*num_rows-1)), pd.DataFrame(current_vol_list).T], axis=0)
        print("After adding new record, the df_vols has %d records" % len(df_vols))
        average_vol1 = df_vols.iloc[:int(num_rows), :].mean(numeric_only=True, axis=0).tolist()
        average_vol2 = df_vols.iloc[int(num_rows):, :].mean(numeric_only=True, axis=0).tolist()
        assert isinstance(average_vol1, list)
        assert isinstance(average_vol2, list)
        return average_vol1, average_vol2, df_vols, num_rows, len(df_vols)


def volume_change(vol1, vol2, threshold):
    """ This function compares two list, return True if
    at least one of the tank volume changed more than 50 tons """
    print("Vol1: ", vol1[:5])
    print("Vol2: ", vol2[:5])
    print("The change of the first five values: ", [abs(a - b) for a, b in zip(vol1, vol2)][:5])
    print("The max change is :", max([abs(a-b) for a, b in zip(vol1, vol2)]))
    if max([abs(a-b) for a, b in zip(vol1, vol2)]) >= threshold:
        print("at least one volume has changed more than %d" % threshold)
        return True
    else:
        print("no volume has changed more than %d" % threshold)
        return False


def write_file(data, logpath, filename, header):
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
    with open(my_file, write_mode) as f:
        df = pd.DataFrame(data).T
        df.columns = header
        df.to_csv(f, index=None, header=if_header)


def main(logpath, sample_rate, sample_period=60):
    """This function logs the volume to a csv file when:
    compared with last minute average
    at least one of the tank volume changed more than 50 tons
    """
    df_vols = pd.DataFrame()
    start_time = time.time()
    while True:
        # There should be a function detecting user input for switching mode.
        with open(mode_file,'r') as f:
            log_mode = f.read()

        print("\n")
        print("Start")
        #if log_mode == "LOAD" :
            # sample_period = 10

        time.sleep(60 / sample_rate)
        print("It's %s mode" %log_mode)
        tanknames = tanklist(reading_plus_file)
        vol_daily_file = str(datetime.datetime.now().strftime("%Y-%m-%d")) + str("_vol_m3.csv")

        average_vol1, average_vol2, df_vols, num_rows, len_df_vols = read_volume(df_vols, reading_plus_file, sample_period, sample_rate)
        print("Now the live data for average has %d items" % len_df_vols)
        if len_df_vols < num_rows*2:
            print("This is the %d value, we need %d values to start logging" %(len_df_vols, num_rows*2))
            continue

        current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_vol_list = [current_date_time] + [log_mode] + average_vol2
        print("length of current_data_list", len(average_vol2))
        print("length of the data to log:", len(current_time_vol_list))
        log_header = ["Time"] + ["log_mode"] + tanknames
        print("length of the header",len(log_header))

        if volume_change(average_vol1, average_vol2, 50) or log_mode == "LOAD":
            write_file(current_time_vol_list, logpath, vol_daily_file, log_header)
            print("new value has been logged")
        else:
            print("not logged")


if __name__ == "__main__":
    main(logpath, 30)  # logpath, sample_rate (no.of readings per minute), by default read measurement every 2 second


