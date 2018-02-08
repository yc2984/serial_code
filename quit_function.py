import sys, time, msvcrt


def readInput(timeout = 2):
    start_time = time.time()
    #sys.stdout.write('%s:'%(caption));
    # input_value = '' #initially blank
    if msvcrt.kbhit():  #Return true if a keypress is waiting to be read.
        chr = msvcrt.getche()
        if ord(chr) == 113: # Latin Small Letter Q
            return 0
        else:
            return 1
    else:
        return 1

        #if len(input_value) == 0 and (time.time() - start_time) > timeout:
        #    continue

#    print ('' ) # needed to move to next line
#   if len(input_value) > 0:
#        return input_value   #only if the input is q, the program stops. input = 'q'
#    else:
#        return default  #all the other cases, the program continues. default = 'continue'


# and some examples of usage
while True:
    answer = readInput()
    if answer == 0:
        break
#print ('The name is %s' % ans)
