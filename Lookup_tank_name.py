import pandas as pd

table = pd.read_csv(r"C:\Users\Yang\Documents\RBES work\Projects&study\Sensors\Reference\GLM_Info\sensor_id_tankname_vol.csv")


def id_to_tankname(id):
    """ This function looks up the tank name by sensor ID, returns a list of tanknames"""
    tankname = table.loc[table["sensor_id"] == id,"tankname"].tolist()
    if len(tankname) >= 1:
        tankname = tankname[0]
        return tankname
    return "draft"


def tanklist(vol_file):
    df_current_vol = pd.read_csv(vol_file, header=None)
    ids = df_current_vol.iloc[:, 0]
    tanknames = []
    for id in ids:
        tankname = id_to_tankname(id)
        tanknames.append(tankname)
        #print("sensor", id, ":", tankname)
        #print(type(tankname))
        #print(len(tankname))
    #print("length of tanknames:",len(tanknames))
    #print("Type of tanknames:",type(tanknames))
    return tanknames

