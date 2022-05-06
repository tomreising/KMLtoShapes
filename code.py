"""

see https://stackoverflow.com/questions/70965145/can-plotly-for-python-plot-a-polygon-with-one-or-multiple-holes-in-it
for example of how ploting works for shapely shapes


Created on Fri May  6 11:54:39 2022


"""
import xml.etree.ElementTree as ET
import re
from shapely.geometry import Polygon
from plotly.offline import plot
import plotly.graph_objects as go
import plotly.express as px
import json

def getkmlshapes(path):
    with open(path, 'r') as f:
        xmlString = f.readlines()
    f.close()
    xmlString = "\n".join(xmlString)
    xmlString = re.sub("<\?[\w\W]*?>","",xmlString)
    xmlString = re.sub("<kml[\w\W]*?>","",xmlString)
    xmlString = re.sub("</kml[\w\W]*?>","",xmlString)
    tree = ET.fromstring(xmlString)
    #shapes = []
    polygonShape = {}
    for n,item in enumerate(tree.iter('Polygon')):
        outerBoundList = []
        for outerShape in item.iter('outerBoundaryIs'):
            for outerCoords in outerShape.iter('coordinates'): #should only have one outer coordinate per polygon
                coordText =  outerCoords.text
                coordList = coordText.split(" ")
                coordList = [i.strip()  for i in coordList if len(i.strip()) > 3]
                for latlong in coordList:
                    innerList = []  
                    coordSplit = latlong.split(',')
                    for n2,z in enumerate(coordSplit):
                        y = z.strip()
                        if n2 !=2:
                            innerList.append(float(y))
                    outerBoundList.append(innerList)
        holesList = []
        for n3,innerShapes in enumerate(item.iter('innerBoundaryIs')):
            midlist = []
            for innerCoords in innerShapes.iter('coordinates'): 
                coordText =  innerCoords.text
                coordList = coordText.split(" ")
                coordList = [i.strip()  for i in coordList if len(i.strip()) > 3]
                for latlong in coordList:
                    innerList = []  
                    coordSplit = latlong.split(',')
                    for n4,z in enumerate(coordSplit):
                        y = z.strip()
                        if n4 !=2:
                            innerList.append(float(y))
                    midlist.append(innerList)
            holesList.append({'hole_'+str(n3) : midlist})
        polygonShape.update({'poly_' + str(n) : {'outerShape' : outerBoundList, 'holes' : holesList}})
    return polygonShape


def genPolyList(kmlShapes):
    MyPolys = []
    for cnt,key in enumerate(y.keys()):
        HolesList = []
        PolyShape = [tuple(i) for i in kmlShapes[key]['outerShape']]
        for items in kmlShapes[key]['holes']:
            for cordlists in items.values():
                HolesList.append([tuple(i) for i in cordlists])
        MyPolys.append(Polygon(PolyShape, HolesList))
    return MyPolys

def genGeoRefs(polyList, rgba = "rgba(255, 102, 102,0.175)"):
    geoRefs = []
    for items in polyList:
        geoRefs.append({"source": items.__geo_interface__, "type": "fill", "color": "rgba(255, 102, 102,0.175)"})
    return geoRefs



y = getkmlshapes(r"filepath.kml")
q = genPolyList(y)
myGeosRefs = genGeoRefs(q)

fig = px.scatter_mapbox(lat=[0], lon=[0], mapbox_style="carto-positron",width=1000, height=800).update_layout(

    mapbox={
        "zoom": 2,
        "layers": myGeosRefs
    }
)


plot(fig)


#####################################
### create geoJson File #############
#####################################


featuresList = []
for items in q:
    featuresList.append({
        "type": "Feature",
        "properties": {
          "color": "rgba(255, 102, 102,0.175)",
          },
        "geometry": items.__geo_interface__
    })

geoJson = {
      "type": "FeatureCollection",
      "features": featuresList
      }


with open(r'filepath.json', 'w') as outfile:
    json.dump(geoJson, outfile)
