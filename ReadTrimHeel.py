from Path_file_names import readonly_path, trimheel_filename, COM_trimheel
import serial
import os
import time

savepath = readonly_path
filename = trimheel_filename
samplerate = 1   
ind = 0

ser = serial.Serial(
    port=COM_trimheel,\
    baudrate=9600,\
    parity=serial.PARITY_NONE,\
    stopbits=serial.STOPBITS_ONE,\
    bytesize=serial.EIGHTBITS)

print("connected to: " + ser.portstr)


# write logfile 
def write_file(data,filename):
    """
    this function write data to the logfile
    :param data:
    :return:
    """
    
    with open(os.path.join(savepath,filename), 'w') as f:  # open logfile 
        f.write(data)               # write concatenate databatch to logfile 
        f.close()                   # close logfile 

starttime = time.time()             # starttime for measurement loop


while True:
    try:
        bytes = ser.readline()
    except:
        print("Couldn't receive the trim heel data")
        continue
    str1 = bytes.decode('utf-8')
    print('You received: ' + bytes.decode('utf-8'))
    if ' ' in str1 and len(str1) == 18: 
        s0 = str1.split()[0]
        s0 = s0[1:]
        s1 = str1.split()[1]
        s1 = s1[1:]
        data = s0 + "," + s1
        write_file(data,filename) 
        print("new value written")
        if len(data) == 13:
            write_file(data,filename) 
            print('run: ' + str(ind) + ' datastring: ' + data)
        else:
            print('run: ' + str(ind) + ' datastring: FAIL')
    else:
        print('run: ' + str(ind) + ' datastring: FAIL2')
        print(len(str1))

    time.sleep(samplerate - ((time.time() - starttime) % samplerate))
    ind = ind+1
    len(str1)
    
