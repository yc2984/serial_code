# https://stackoverflow.com/questions/47926257/can-i-read-modbus-rs485-data-received-on-a-slave-computer-with-python
import sys
import os
import time
import datetime
import pandas as pd
import numpy as np
from pandas.util.testing import assert_series_equal
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import serial

PORT = 'COM10'


# PORT = '/dev/ptyp5'

def write_file(time_data, data, logpath, filename):
    with open(os.path.join(logpath, filename), 'a', encoding="utf-8") as f:  # open log file
        f.write(str(time_data) + "," + str(data) + '\n')
        f.close()


logpath = r'C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\serial_code'
filename = 'test_output.txt'


def main():
    """main"""
    logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s")

    # Create the server
    server = modbus_rtu.RtuServer(serial.Serial(PORT))

    try:
        logger.info("running...")
        logger.info("enter 'quit' for closing the server")

        server.start()

        slave_1 = server.add_slave(1)
        slave_1.add_block('block1', cst.HOLDING_REGISTERS, 100, 127)  # According to Excelsheet of Siemens.
        slave_1.set_values('block1', 100, 127 * [0])  # Initiate the values
        slave_1.set_values('block1', 100, 255)  # PLC--第0011寄存器的初始值为高八位全为0，低八位全为1
        # construct a DataFrame for data logging (log all the data in the DataFrame, only write the changed data)
        values = pd.DataFrame()
        date_time_series = pd.Series()
        while True:

            #cmd = sys.stdin.readline()
            #print(cmd)
            #args = cmd.split(' ')

            #Read current date time
            time.sleep(3)  # wait for 2 seconds
            current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #print("current time:" + str(current_date_time))
            date_time_series = pd.concat([date_time_series,pd.Series(current_date_time)]) #not needed

            #Read current value
            value = slave_1.get_values('block1', 100, 127)
            list_value = list(value)
            print('current value' + str(value)) #tuple

            list_value.insert(0,current_date_time)  #inserted the datetime, INPLACE. So list_value actully includes the datetime.
            print("time_and_value:"+str(list_value))
            print("length of the time and value:" + str(len(list_value)))

            #Log the current value into DataFrame
            values = pd.concat([values, pd.DataFrame(list_value).T], axis=0)
            values.index = date_time_series
            print("This is the logging dataframe") #logging all the readings.
            print(values.head())

            # only write the changed values to txtfile
            # Check if it's the first reading of this record.
            #if values.empty:
            if len(values) == 1:

                write_file(current_date_time, value, logpath, filename)
                # check the dimension and the last row of values DataFrame
                print("The dimension of values DataFrame: %s" %(values.shape,))
                print("The last row of values DataFrame" + str(values.iloc[-1, :]))
                continue

            # compare if the new reading is the same as the last recorded
            df_temp = pd.DataFrame({"Last_row_values": values.iloc[-2, :], "New_reading": pd.Series(list_value)})
            print("This is the comparison DataFrame")
            print(df_temp.head())
            if (df_temp.loc[1:,'Last_row_values'] == df_temp.loc[1:,'New_reading']).all(): #Don't compare the time.
                print("The value has not changed since last time, not recorded")
                continue

            #values = pd.concat([values, pd.DataFrame(list(value)).T], axis=0)
            write_file(current_date_time, value, logpath, filename)
            print("The new value is recorded")

            #if cmd.find('quit') == 0:
            #    sys.stdout.write('bye-bye\r\n')
            #break

    finally:
        server.stop()


if __name__ == "__main__":
    main()
