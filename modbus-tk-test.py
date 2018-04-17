import sys
import os
import time
import datetime
import pandas as pd
import numpy as np
import csv
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu, hooks
import serial
import logging
PORT = 'COM10'
# PORT = '/dev/ptyp5'

logpath = r'C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\Log'
filename_long = 'all_output.csv'


def write_file(data, logpath, filename, header, if_header, mode):  # Append new record to a csv file.
    with open(os.path.join(logpath, filename), mode) as f:
        df = pd.DataFrame(data).T
        df.columns = header
        df.to_csv(f, index=None,header = if_header)
    # with open(os.path.join(logpath, filename), 'a', encoding="utf-8") as f:  # open log file
        #f.write(str(data) + '\n')
        #f.close()


glmpath = r'C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\GLM_maker_test\GLM_test'
glmtxt = 'glminput.txt'


def write_glm_feed(data, glmpath, glmtxt):  # glm is a hydrostatic software
    data.to_csv(os.path.join(glmpath, glmtxt), index=False,header=None, mode='w')


trimheel_path = r'C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\Read_trim_heel'
trimheel_filename = 'trimheel.txt'


def read_trimheel(trimheel_path,trimheel_filename):
    with open(os.path.join(trimheel_path,trimheel_filename),'r') as th:
        trimheel = list(th.read().split(","))


def main():
    """main"""
    logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s",level=logging.DEBUG)
    # logger.setLevel(logging.DEBUG)
    # Create the server
    server = modbus_rtu.RtuServer(serial.Serial(PORT))
    server.set_verbose =True

    # Read sensor ID, tank names and initial tank values from a file.
    # Initialize the values with example txt from Stephane.
    df_sensor_ID = pd.read_csv(r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\Reference\GLM_Info\Sensor_ID_Tank_name.csv",header=None)
    sensor_ID = df_sensor_ID.loc[:, 0]
    initial_values = df_sensor_ID.iloc[:, 1].tolist()  # the second column is the initial values
    Tank_names = df_sensor_ID.iloc[:, 2].tolist()
    # Initiate a DataFrame with only tank names for data logging (log all the data in this DataFrame)
    values_header = ["Time"] + Tank_names
    values = pd.DataFrame()

    try:
        logger.info("running...")
        logger.info("enter 'quit' for closing the server")

        def log_data(data):
            server, bytes_data = data
            logger.info(bytes_data)

        hooks.install_hook('modbus_rtu.RtuServer.after_read', log_data)
        hooks.install_hook('modbus_rtu.RtuServer.before_write', log_data)

        server.start()
        print("server started")
        slave_1 = server.add_slave(1) # GLM ignore value > 65437
        # slave_1 = server.add_slave(1, unsigned=False)
        print("slave_1 is added")
        slave_1.add_block('block1', cst.HOLDING_REGISTERS, 99, 127)  # Pressure values, PLC write to GLM
        slave_1.add_block('block2', cst.HOLDING_REGISTERS, 299, 79)   # volume values, PLC read from GLM
        print("holding registers are added")

        slave_1.set_values('block1', 99, initial_values)  # Initiate the values with the txt from Stephane
        slave_1.set_values('block2', 299, 79 * [400])

        date_time_series = pd.Series()
        start_time = time.time()
        while time.time() - start_time < 120:  # 1 min timer

            hooks.install_hook('modbus_rtu.RtuServer.after_read', log_data)
            hooks.install_hook('modbus_rtu.RtuServer.before_write', log_data)

            #cmd = sys.stdin.readline()
            #print("cmd is:"+str(cmd))
            # args = cmd.split(' ')
            # Read current date time
            #answer = input('please enter quit to stop the program\n')
            time.sleep(5)  # wait for 2 seconds for the possible user input "quit"
            #if answer == "quit":
            #    break

            current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # to insert before value list
            date_time_series = pd.concat([date_time_series, pd.Series(current_date_time)]) #for index of values dataframe

            # Read current Pressure value, written by PLC
            value = slave_1.get_values('block1', 99, 127)  # value type: tuple

            # WRITE GLM FEED
            df_current_value = pd.DataFrame({'Sensor_ID': sensor_ID, 'Sensor_reading': value})  # tuple
            write_glm_feed(df_current_value, glmpath, glmtxt)

            # Insert the timestamp of current value, INPLACE.
            list_value = list(value)
            list_value.insert(0,current_date_time)
            print("length of the timestamp and current value, should be 128:" + str(len(list_value)))

            # Append every timestep (5s)'s timestamp& current value to the values DataFrame
            values = pd.concat([values, pd.DataFrame(list_value).T], axis=0)  # concat by row i.e. append new record.
            #values.index = date_time_series
            print("This is the dataframe with all readings")
            print("The shape of the logging dataframe is" + str(values.shape))
            print(values.head())

            # Create a new log file every hour
            filename = str(datetime.datetime.now().strftime("%Y-%m-%d_%H"))+str("h.csv") # new file every hour
            print(filename)
            # Log value change >50 mmH2o
            # Check if it's the first reading of this record.
            if len(values) == 1:
                write_file(list_value, logpath, filename,values_header,True,'w+')
                # check the dimension and the last row of values DataFrame
                print("The dimension of values DataFrame: %s" % (values.shape,))
                print("The last row of values DataFrame" + str(values.iloc[-1, :]))
                continue

            # Construct a temp df to compare the last two readings
            df_temp = pd.DataFrame({"Last_row_values": values.iloc[-2, :], "New_reading": pd.Series(list_value)})
            print("This is the comparison DataFrame")
            print(df_temp.head())
            # If the change is less than 50, don't write to file
            if max(abs(df_temp.loc[1:, 'Last_row_values'] - df_temp.loc[1:, 'New_reading'])) <  50:  # Don't compare the time.
                print("The pressure has not changed more than 50 mm H2O, not recorded")
                continue
            # The change is more than 50, write to file
            write_file(list_value, logpath, filename,values_header,False,'a')
            print("The new value is recorded")

            #if cmd.find('quit') == 0:
            #if 'quit' in cmd:
            #    sys.stdout.write('bye-bye\r\n')
            #break
        #write all the readings of this log to a txt file
        #values.to_csv(os.path.join(glmpath, filename_long),index=None)
    finally:
        values.to_csv(os.path.join(logpath, filename_long), index=None,header = values_header)
        print("Time is up")
        server.stop()


if __name__ == "__main__":
    main()
