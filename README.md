
![Cover](https://github.com/sctongye/EDGT/blob/master/static/img/cover.jpg?raw=true "Cover")

## ERPIMS Data Geoprocessing Tool

ERPIMS (Environmental Resources Program Information Management System) database was designed by a multidisciplinary team of professionals consisting of hydrogeologists, chemists, applied statisticians, system analysts and environmental project managers to provide additional information that is required by users, incorporate information from the AFCEC Quality Assurance Project Plan and support initiatives of the Defense Environmental Security Corporate Information Management (DESCIM) Program Management Office (PMO).

For database structure questions, please refer to the [Air Force Civil Engineer Center ERPIMS Data Loading Handbook Introduction](http://synectics.net/public/erpims_2013_dlh/index.html).

This EDGT (ERPIMS Data Geoprocessing Tool) system I developed is aimed to help ERPIMS user to visualize data with  open-source geographic information based programming libraries. With EDGT, users are able to geoprosess the chemical datasets into GeoJSON (format for encoding a variety of geographic data structures) format categorized by chemical of interests and/or matrix, frontend developers will be able to use it to build web-based GIS interface for analysis.

This system is open sourced, users are encouraged to modify based on their own needs to optimize the geoprosessing results.

[<img src="https://github.com/sctongye/EDGT/blob/master/static/img/buy-me-a-coffee-button.png" width="100">](https://www.buymeacoffee.com/jiayuwang)

### Installation

Access databases (file-based databases) works as core in data transition in this tool, Windows machine is recommended to use. 

#### Platform
Windows OS with Microsoft Office installed. Microsoft Access Driver is need. Make sure the ODBC drivers provided by ACEODBC.DLL are listed in the Select a driver dialog box.

Affected drivers:
```
Microsoft Access Driver (*.mdb, *.accdb)
Microsoft Access Text Driver (*.txt, *.csv)
Microsoft Excel Driver (*.xls, *.xlsx, *.xlsm, *.xlsb)
Microsoft Access
Microsoft Excel
```

Mac and/or other Unix/Linux based platforms are not suggested. On Linux, the mdbtools package provides some degree of compatibility with the `.mdb` file format, allowing such a database to be queried and modified by a Linux application directly. Another Open Source library (Java) for manipulating (`.mdb` and `.accdb`) databases is jackcess.

Once the requested ERPIMS database is issued and received from the AFCEC, rename the `.mdb` file with LDI database in it and save into /apps/ERPIMS/MDB/ directory. If the files you received include 4 or more pieces of database files, that means all of them except for the one includes LDI info are for chemical results, try to migrate all data into one `.mdb` or `.accbd` file and link it to the main ERPIMS `.mdb`.

Clone this repository:
```
git clone https://github.com/sctongye/EDGT.git
```
cd into EDGT.
Install virtualenv.
Install Python 3.6 and Django 3.0.4.
Create a new virtualenv, run:
``` 
$ pip install -r example-requirements.txt
```

```
asgiref==3.2.7
Django==3.0.4
mysqlclient==1.4.6
Pillow==7.0.0
pytz==2019.3
sqlparse==0.3.1
pandas==0.25.3
pyodbc==4.0.30
pyproj==2.6.0
numpy==1.18.1
```
Create the database:
```
$ python manage.py migrate --run-syncdb
```
Finally, run the development server:
```
$ python manage.py runserver
```

### Projection Converting
For most of the ERPIMS database, longitude and latitude (are already input in LDI data table), users are able to use them directly. If you find out x/y are not fully provided and would like to use ECOORD and NCOORD instead, function below can be used for coordinate converting.

*python3*
```python
from pyproj import CRS, Transformer

def convertXY(row, latlng=None):
    proj_in = CRS("EPSG:4326")
    proj_out = CRS("EPSG:4326")
    transformer = Transformer.from_crs(proj_in, proj_out)
    lat, long = transformer.transform(row['X_COORD'], row['Y_COORD'])
    if latlng == "lat":
        return lat
    elif latlng == "lng":
        return long
    else:
        return lat, long
```
*python2* (If ArcGIS is installed)
```python
import arcpy

raw_data_proj = xxxx
rawSR = arcpy.SpatialReference(raw_data_proj) 
outputSR = arcpy.SpatialReference(4326)
point = arcpy.Point(rawX, rawY)
point_geom = arcpy.PointGeometry(point, rawSR)
proj_point = point_geom.projectAs(outputSR)
x2, y2 = (proj_point.firstPoint.X, proj_point.firstPoint.Y)
```