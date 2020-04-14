from django.shortcuts import render, redirect
from django.http import HttpResponse
import os, pyodbc, json
import pandas as pd
import numpy as np
from EDGT.settings import BASE_DIR
from django.views import View
try:
    import map_conf
except:
    pass
import datetime

LATEST_MDB_FILE_NAME = "Processing.mdb"

LATEST_MDB_FILE_NAME = LATEST_MDB_FILE_NAME.replace(".mdb", "") + ".accdb"
LATEST_MDB = os.path.join(os.path.dirname(__file__), "MDB", LATEST_MDB_FILE_NAME)
# print(LATEST_MDB)

def get_conn(mdb):
    MDB = mdb
    DRV = '{Microsoft Access Driver (*.mdb, *.accdb)}'
    PWD = 'pw'
    conn = pyodbc.connect('DRIVER={};DBQ={};PWD={}'.format(DRV, MDB, PWD))
    print("Connecting Database - {0} .....".format(MDB.split('\\')[-1]))
    return conn


def df_to_geojson(df, properties, lat='NCOORD', lon='ECOORD'):
    """
    Turn a dataframe containing point data into a geojson formatted python dictionary

    df : the dataframe to convert to geojson
    properties : a list of columns in the dataframe to turn into geojson feature properties
    lat : the name of the column in the dataframe that contains latitude data
    lon : the name of the column in the dataframe that contains longitude data
    """

    # create a new python dict to contain our geojson data, using geojson format
    geojson = {'type': 'FeatureCollection', 'features': []}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type': 'Feature',
                   'properties': {},
                   'geometry': {'type': 'Point',
                                'coordinates': []}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row[lon], row[lat]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]

        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)

    return geojson


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


# MATRIX: Air, SE, SO, SW, GW
def process_data(MDB, MATRIX):
    conn = get_conn(MDB)
    cursor = conn.cursor()

    try:
        sql_delete_data = 'DROP TABLE %s_data;'%(MATRIX)
        cursor.execute(sql_delete_data)
        conn.commit()
    except:
        pass

    sql = "{CALL %s}"%(MATRIX)

    crsr = conn.execute(sql)
    conn.commit()


    sql = 'SELECT * FROM %s_data;'%(MATRIX)
    df = pd.read_sql(sql, conn)

    df.loc[df['End_depth'] == 0, ['Start_Depth', 'End_depth']] = ''
    df['Month'] = pd.DatetimeIndex(df['SampDate']).month
    df['Year'] = pd.DatetimeIndex(df['SampDate']).year
    df['Day'] = pd.DatetimeIndex(df['SampDate']).day
    df['SampID'] = df['LOCID'] + '_' + df['Start_Depth'].map(str) + '_' + df['End_depth'].map(str) + '_' + df['Month'].map(str) + '/' + df['Day'].map(str) + '/' + df['Year'].map(str) + '_' + df['SACODE'] + '_' + df['MATRIX'] + '_' + df['PARLABEL']
    df = df.sort_values(by='NF_Result', ascending=False)
    df = df.drop_duplicates(["SampID"], keep="first")
    crsr.close()
    conn.close()
    # print(df)

    # columns = df.columns.tolist()
    print(df.columns.tolist())
    columns = ["LOCID", "NCOORD", "ECOORD", "Start_Depth", "End_depth", "SACODE", "SampDate", "MATRIX", "NF_Result", "Unit"]
    geojson_dict = df_to_geojson(df, properties=columns)
    geojson_str = json.dumps(geojson_dict, indent=2, default = myconverter)
    output_filename = '%s.geojson'%(MATRIX)
    output_filename = os.path.join(BASE_DIR, "static", "data", output_filename)
    with open(output_filename, 'w') as output_file:
        output_file.write(geojson_str)

    x_min = min(df['ECOORD'])
    x_max = max(df['ECOORD'])
    y_min = min(df['NCOORD'])
    y_max = max(df['NCOORD'])
    original_x = (x_min + x_max) / 2
    original_y = (y_min + y_max) / 2
    map_center = [original_y, original_x]
    print(map_center)

    if MATRIX == "GW":
        mapconf_filename = os.path.join(BASE_DIR, "apps", "ERPIMS", "MDB", "map_conf.py")
        with open(mapconf_filename, 'w') as output_file:
            output_file.write("map_center = %s"%(map_center))

    # map_center = map_conf.map_center

    # df_air = pd.read_sql(sql_air, conn)
    # df_se = pd.read_sql(sql_se, conn)
    # df_so = pd.read_sql(sql_so, conn)
    # df_sw = pd.read_sql(sql_sw, conn)
    # df_gw = pd.read_sql(sql_gw, conn)

    # print(df_air)
    # print(df_se)
    # print(df_so)
    # print(df_sw)
    # print(df_gw)


class IndexView(View):
    def get(self, request):
        return render(request, "index.html")


class MakeUpdate(View):
    def get(self, request):
        # for matrix in ["Air", "SE", "SO", "SW", "GW"]:
        #         #     process_data(LATEST_MDB, matrix)
        process_data(LATEST_MDB, "SE")
        return HttpResponse("完成更新")


process_data(LATEST_MDB, "SO")


# for matrix in ["Air", "SE", "SO", "SW", "GW"]:
#     process_data(LATEST_MDB, matrix)
# process_data(LATEST_MDB, "SO")

# for matrix in ["Air", "SE", "SO", "SW", "GW"]:
#     process_data(LATEST_MDB, matrix)


