#https://stackoverflow.com/questions/47926257/can-i-read-modbus-rs485-data-received-on-a-slave-computer-with-python
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
#PORT = '/dev/ptyp5'

def write_file(time_data,data,logpath,filename):
    with open(os.path.join(logpath, filename), 'a',encoding="utf-8") as f:  # open log file
        f.write(str(time_data)+","+str(data)+'\n')
        f.close()

logpath = r'C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\serial_code'
filename = 'test_output.txt'

def main():
    """main"""
    logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s")

    #Create the server
    server = modbus_rtu.RtuServer(serial.Serial(PORT))

    try:
        logger.info("running...")
        logger.info("enter 'quit' for closing the server")

        server.start()

        slave_1 = server.add_slave(1)
        slave_1.add_block('block1', cst.HOLDING_REGISTERS, 100, 127) #According to Excelsheet of Siemens.
        slave_1.set_values('block1', 100, 127 * [0]) #Initiate the values
        slave_1.set_values('block1', 100, 255)  # PLC--第0011寄存器的初始值为高八位全为0，低八位全为1
        #construct a dataframe for storing data
        values = pd.DataFrame()
        while True:
            time.sleep(2) #wait for 2 seconds
            Current_date_time = datetime.datetime.now()
            print("current time:"+str(Current_date_time))
            #cmd = sys.stdin.readline()
            #print(cmd)
            #args = cmd.split(' ')

            value = slave_1.get_values('block1', 100, 127)

            print('current value'+ str(value))
            #print("type of value: " + str(type(value))) #tuple

            #Check if the value is different than the last one.
            if values.empty:
                values = pd.concat([values,pd.DataFrame(list(value)).T],axis=0)  #good!
                write_file(Current_date_time, value, logpath, filename)
                #check the dimension of values dataframe
                print("values dataframe dimension"+str(values.shape))
                print("The last row of values"+str(values.iloc[-1, :]))
                continue
            if assert_series_equal(pd.Series(list(value)), values.iloc[-1,:]):
                print("The value has not changed since last time")
                continue
            values = pd.concat([values, pd.DataFrame(list(value)).T], axis=0)
            write_file(Current_date_time, value, logpath, filename)
            print(values)

                #value.write(r'','a')

                #if cmd.find('quit') == 0:
                    #sys.stdout.write('bye-bye\r\n')
                    #break

    finally:
        server.stop()

if __name__ == "__main__":
    main()