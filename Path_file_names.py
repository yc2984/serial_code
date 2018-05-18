import os
# This file contains all the path used in the program.

#####################################################
# Please change accordingly
# Set up com port
COM_modbus = "COM10"
COM_trimheel = "COM11"

# Path for logging
logpath = r'C:\GLM_logging\Logs'

# The read only path
readonly_path = r'C:\GLM_logging\ReadOnly'

# glm program path
glmpath = r'C:\GLM_logging\AUDAX_test_v16'


sample_rate = 60
sample_period = 60


###################################################
# Please don't touch this part

glmtxt = 'READINGS.txt'
reading_plus_file = os.path.join(glmpath, "READINGS+.TXT")

# file contains sensor ID, example reading and tank names.
initial_info = os.path.join(readonly_path, "Sensor_ID_Tank_name2.csv")

# The file name that stored trim heel file.
trimheel_filename = 'trimheel.txt'

#mode_file
mode_file = os.path.join(readonly_path, "mode.txt")

# sensor id and tank name correspondence from glm.
glm_id_name = os.path.join(readonly_path, "sensor_id_tankname_glm.csv")