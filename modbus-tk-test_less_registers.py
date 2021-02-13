import os
import time
import datetime
import pandas as pd
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu, hooks
import serial
import logging
from pathlib import Path
from Path_file_names import mode_file, logpath, readonly_path, trimheel_filename, glmpath, glmtxt, initial_info, COM_modbus, sample_period, sample_rate
PORT = COM_modbus


def read_sensor_id():
    # Read PLC register id(100 - 235 + 227 & 228 (repeated, for trim& heel)), description (Tank_names),
    #  and initial values from a file.
    # Initialize the pressure values with example txt from Stephane.
    df_sensor_id = pd.read_csv(initial_info, header=None)
    register_id = df_sensor_id.loc[:, 0].tolist()
    initial_regi_values = df_sensor_id.iloc[:, 1].tolist()  # the second column is the initial values
    regi_names = df_sensor_id.iloc[:, 2].tolist()

    sensor_id = register_id[0:129]
    Tank_names = regi_names[0:129]
    initial_pa = initial_regi_values [0:129]
    return sensor_id, Tank_names, initial_pa, initial_regi_values


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


def write_glm_feed(sensor_id, data, glmpath, glmtxt):  #  data should be a list, length both 129.
    glm_feed_table = pd.DataFrame({"sensor_id": sensor_id, "p_and_a": data})
    cols = ["sensor_id","p_and_a"] # Make sure the order of the columns is correct.
    glm_feed_table = glm_feed_table[cols]
    glm_feed_table.to_csv(os.path.join(glmpath, glmtxt), index=False, header=glm_feed_table.columns, mode='w')


def read_trim_heel(trimheel_path, trimheel_filename): # read trim, heel from a textfile
    with open(os.path.join(trimheel_path,trimheel_filename), 'r') as th:
        try:
            trim_heel = list(th.read().split(","))
            trim_heel = [float(x) for x in trim_heel]
            print("The length of trim_heel: ",len(trim_heel))
            print("data type trim",type(trim_heel[0]))
            return trim_heel
        except ValueError:
            return [0,0]


def live_table(df_pa_live, current_pa_list, sensor_id, sample_period, sample_rate):
    """
    df_pa_live: a pre-defined empty table
    current_pa_list: pressure& trimheel, refreshed every second, 129 items
    sensor_id: the sensor id that corresponds to the sequence of modbus readings. 129 items
    sample_period: the period that user want to average on
    sample_rate: the number of readings every minute.

    1. For normal mode, to construct a live table containing 1 minute (or user defined period) data.
    2. refresh every second
    3. returns
        (1) average pressure of the last minute every minute. otherwise return None
        (2) the live table
        (3) the number of rows required to start logging (depends on sample period & rate)
        (4) the number of rows in current live table

    """
    num_rows = sample_period/(60/sample_rate) # If sample_rate = 60, sample period 60 seconds, num_rows is 60.
    print("%d values will be used for average" % num_rows) # #of rows required
    print("Before adding new record, the df_vols has %d records" % len(df_pa_live))

    if len(df_pa_live) < num_rows - 1:  # accumulate the first minute to get an average.
        df_pa_live = pd.concat([df_pa_live, pd.DataFrame(current_pa_list).T], axis=0)
        print("After adding new record, the df_vols has %d records" % len(df_pa_live))
        return None, df_pa_live, num_rows, len(df_pa_live)  # The length after append current reading.
    else:
        df_pa_live = pd.concat([df_pa_live.tail(int(num_rows-1)), pd.DataFrame(current_pa_list).T], axis=0)
        print("After adding new record, the df_vols has %d records" % len(df_pa_live))
        ave_pa_list = df_pa_live.mean(numeric_only=True, axis=0).tolist()
        print("ave_pa_list has %d elements (should be 129)" %len(ave_pa_list))
        assert isinstance(ave_pa_list, list)
        # Create a table for glm_write
        print(df_pa_live[:5])
        return ave_pa_list, df_pa_live, num_rows, len(df_pa_live)


def modejudge(modes_list): #the list of treatmode & pump status
    if max(modes_list[1:]) == 1:
        log_mode = "LOAD"
    elif modes_list[0] != 0:
        log_mode = "LOAD"
    else:
        log_mode = "NORMAL"
    with open(mode_file,'w') as f:
        f.write(log_mode)
    return log_mode


def main(logpath, sample_rate, sample_period=60):
    """main
    Workflow:
    1. Create server (where slave stays on)
    2. Initialize the sensor id , tanknames, initial pressure values, trimheel, treatmodes, pump status.
    3. try to start server
    4. loop every seconds to get new readings from modbus.
    5. judge log mode by treatmode and pump status, and decide what to output.
    """

    # Create logger and server
    logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s",level=logging.DEBUG)
    server = modbus_rtu.RtuServer(serial.Serial(PORT, 19200))
    server.set_verbose(True)

    # Read register_id, regi_names and initial values from a file.
    sensor_id, Tank_names, initial_pa, initial_regi_values = read_sensor_id()

    # Prepare empty table for further usage.
    df_pa_live = pd.DataFrame()

    try:
        logger.info("running...")
        logger.info("enter 'quit' for closing the server")

        #def log_data(data):
            #server, bytes_data = data
            #logger.info(bytes_data)

        #hooks.install_hook('modbus_rtu.RtuServer.after_read', log_data)
        #hooks.install_hook('modbus_rtu.RtuServer.before_write', log_data)

        server.start()
        print("server started")
        slave_1 = server.add_slave(1) # GLM ignore value > 65437, all values are positive
        print("slave_1 is added")
        slave_1.add_block('block1', cst.HOLDING_REGISTERS, 99, 127)  # Pressure values, PLC write to GLM
        slave_1.add_block('block2', cst.HOLDING_REGISTERS, 299, 79)   # volume values, PLC read from GLM
        print("holding registers are added")
        slave_1.set_values('block1', 99, initial_regi_values[:127])  # Initiate the values with the txt from Stephane
        slave_1.set_values('block2', 299, 79*[400])
        # Remember the starting time.
        t0 = time.time()
        counter = 0 # number of valid values received
        while True:
            #hooks.install_hook('modbus_rtu.RtuServer.after_read', log_data)
            #hooks.install_hook('modbus_rtu.RtuServer.before_write', log_data)

            # this defines the frequency of the main loop, in this case every 1 second.
            time.sleep(60 / sample_rate)
            t1 = time.time()
            current_date_time = datetime.datetime.now()
            print("\n")
            print("Start")

            # Read current Pressure value & treatmode & pump status, written by PLC
            current_regi_list = list(slave_1.get_values('block1', 99, 127))  # tuple convert to list
            # Verify the length of input
            try:
                len(current_regi_list) == 127
            except IndexError:
                print("the Input is not the required length")
                continue
            counter += 1

            #split the data into two parts: pressure & modes
            current_press_list = current_regi_list[0:127]
            #current_modes_list = current_regi_list[127:136]
            current_modes_list = [0]*9

            # judge the logging mode
            log_mode = modejudge(current_modes_list)
            print("It's %s mode" % log_mode)

            # Read trim heel values:
            trim_heel = read_trim_heel(readonly_path, trimheel_filename)
            # Combine pressure with trim heel.
            current_pa_list = current_press_list + trim_heel
            # Check the length of the pressure and trim heel record
            print("length of the pressure and trim heel values, should be 129: ", len(current_pa_list))

            # Call the live_table function to get the correspondent feed to feed glm.
            # if normal mode, average p,a; if load or treat mode, realtime p,a
            ave_pa_list, df_pa_live, num_rows, len_df_pa_live = live_table(df_pa_live,
                                                                                current_pa_list,
                                                                                sensor_id, sample_period,
                                                                                sample_rate)
            # Create glm feed
            second = int(t1) - int(t0)
            print("This is %dth second" % second)
            print("This is %dth valid values received" % counter)
            if log_mode == "NORMAL":
                if int(t1) > 1 and counter % sample_period == 0: # log ave_pa per minute.
                    feed_pa_list = ave_pa_list
                    write_glm_feed(sensor_id, feed_pa_list, glmpath, glmtxt)
                    print("######## It's the %dth sample_period, glm feed has been updated" % int(second/sample_period))
                    print("The first five values of glm feed(ave data): ", feed_pa_list[:5])
                else: #  accumulate the live table
                    feed_pa_list = None
                    print("a record has been added to live table")
            else: # Load mode
                assert isinstance(current_pa_list, list)
                feed_pa_list= current_pa_list
                write_glm_feed(sensor_id, feed_pa_list, glmpath, glmtxt) # if load mode, log current_pa_list per second
                print("The first five values of input (real data): ", feed_pa_list[:5])

            # optional logging
            # Create a new log file every day.
            filename = str(current_date_time.strftime("%Y-%m-%d"))+str("_mmH2O.csv")
            assert isinstance(sensor_id, list)
            log_header = ["Time"] + sensor_id
            if log_mode == "LOAD" or feed_pa_list is not None:
                log_pa_list = [current_date_time] + feed_pa_list
                write_file(log_pa_list, logpath, filename, log_header)
            # check the dimension and the last row of values DataFrame
            # print("The dimension of values DataFrame: %s" % (values.shape,))

    finally:
        server.stop()
        print("Server stops")


a = os.getpid()
with open(os.path.join(readonly_path,"pid_modbus-tk-test.txt"),"w") as f:
    f.write(str(a))

if __name__ == "__main__":
    main(logpath, sample_rate, sample_period)
