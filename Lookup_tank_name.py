import pandas as pd
from Path_file_names import glm_id_name

table = pd.read_csv(glm_id_name)

def id_to_tankname(id):
    """ This function looks up the tank name by sensor ID, returns a list of tanknames"""
    tankname = table.loc[table["sensor_id"] == id,"tankname"].tolist()
    if len(tankname) >= 1:
        tankname = tankname[0]
        return tankname
    return "draft"


