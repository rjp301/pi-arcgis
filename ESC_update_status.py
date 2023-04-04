from arcgis import GIS 
from dotenv import dotenv_values
from datetime import datetime, timedelta

import os
import pandas as pd

PATH = os.path.dirname(__file__)
config = dotenv_values(os.path.join(PATH,".env"))
print(datetime.now())

# configure web map symbology to show changes to status field
def update(repairs, monitoring):
    for GlobalID_x in overlap_rows['GlobalID_x']:
        try:
            repairs_feature = [f for f in esc_repair_features if f.attributes['GlobalID'] == GlobalID_x][0]
            monitoring_feature = [f for f in esc_monitoring_features if f.attributes['ParentGuID'] == GlobalID_x][0]
            repairs_feature.attributes['LastMonitored'] = monitoring_feature.attributes['CreationDate']
            repairs_feature.attributes['Status'] = monitoring_feature.attributes['Status']
            esc_repair_lyr.edit_features(updates=[repairs_feature])
            print(f"Updated {repairs_feature.attributes['GlobalID']} status to {monitoring_feature.attributes['Status']}", flush=True)
            print(f"Updated {repairs_feature.attributes['GlobalID']} Last Modified to {monitoring_feature.attributes['CreationDate']}", flush=True)
        except:
            continue
 
gis = GIS("https://www.arcgis.com",
    username=config.get("EMAIL"),
    password=config.get("PASSWORD"),
)
 
one_day = datetime.today() - timedelta(days=1)
string_day = one_day.strftime('%Y-%m-%d %H:%M:%S')
where_query = f"CreationDate >= DATE '{string_day}'"

esc_item = gis.content.get("b314a44f371a4ef5a878da19c86e93f4")

# add esc_monitoring fields to feature layer to hold attributes from related table
esc_monitoring_tbl = esc_item.tables[0]
esc_monitoring_sdf = pd.DataFrame.spatial.from_layer(esc_monitoring_tbl)
esc_monitoring_fset = esc_monitoring_tbl.query(where=where_query)
esc_monitoring_features = esc_monitoring_fset.features

layers = [(0,"lines","ParentGuID2"),(1,"areas","ParentGuID")]

for index,name,ParentGuID in layers:
    # add esc_repair fields to feature layer to hold attributes from related table
    esc_repair_lyr = esc_item.layers[index]
    esc_repair_sdf = pd.DataFrame.spatial.from_layer(esc_repair_lyr)
    esc_repair_fset = esc_repair_lyr.query()
    esc_repair_features = esc_repair_fset.features

    # sorting monitoring layer to find most recent date monitoring date and dropping duplicates and writes values from that record over the feature layer
    df = esc_monitoring_sdf.sort_values('CreationDate', ascending=False)
    df = df.drop_duplicates(subset=ParentGuID)
    overlap_rows = pd.merge(left = esc_repair_sdf, right = df, how='inner', left_on = 'GlobalID', right_on=ParentGuID)
    esc_repair_features = esc_repair_fset.features
    esc_monitoring_updates = esc_monitoring_fset.features
    esc_monitoring_updates.reverse()
    print(overlap_rows)

    for GlobalID_x in overlap_rows['GlobalID_x']:
        try:
            repairs_feature = [f for f in esc_repair_features if f.attributes['GlobalID'] == GlobalID_x][0]
            monitoring_feature = [f for f in esc_monitoring_features if f.attributes[ParentGuID] == GlobalID_x][0]
            repairs_feature.attributes['LastMonitored'] = monitoring_feature.attributes['CreationDate']
            repairs_feature.attributes['Status'] = monitoring_feature.attributes['Status']
            esc_repair_lyr.edit_features(updates=[repairs_feature])

            print(f"Updated {repairs_feature.attributes['GlobalID']} status to {monitoring_feature.attributes['Status']}", flush=True)
            print(f"Updated {repairs_feature.attributes['GlobalID']} Last Modified to {monitoring_feature.attributes['CreationDate']}", flush=True)
        except:
            continue

    print(f'Done for {name}')