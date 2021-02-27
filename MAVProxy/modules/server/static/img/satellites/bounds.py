# -*- coding: utf-8 -*-
from __future__ import division
import math
import requests
import shutil
import os
from PIL import Image
MERCATOR_RANGE = 256

def bound(value, opt_min, opt_max):
  if (opt_min != None): 
    value = max(value, opt_min)
  if (opt_max != None): 
    value = min(value, opt_max)
  return value


def degreesToRadians(deg) :
  return deg * (math.pi / 180)


def radiansToDegrees(rad) :
  return rad / (math.pi / 180)


class G_Point :
    def __init__(self,x=0, y=0):
        self.x = x
        self.y = y



class G_LatLng :
    def __init__(self,lt, ln):
        self.lat = lt
        self.lng = ln


class MercatorProjection :


    def __init__(self) :
      self.pixelOrigin_ =  G_Point( MERCATOR_RANGE / 2, MERCATOR_RANGE / 2)
      self.pixelsPerLonDegree_ = MERCATOR_RANGE / 360
      self.pixelsPerLonRadian_ = MERCATOR_RANGE / (2 * math.pi)


    def fromLatLngToPoint(self, latLng, opt_point=None) :
      point = opt_point if opt_point is not None else G_Point(0,0)
      origin = self.pixelOrigin_
      point.x = origin.x + latLng.lng * self.pixelsPerLonDegree_
      # NOTE(appleton): Truncating to 0.9999 effectively limits latitude to
      # 89.189.  This is about a third of a tile past the edge of the world tile.
      siny = bound(math.sin(degreesToRadians(latLng.lat)), -0.9999, 0.9999)
      point.y = origin.y + 0.5 * math.log((1 + siny) / (1 - siny)) * -     self.pixelsPerLonRadian_
      return point


    def fromPointToLatLng(self,point) :
          origin = self.pixelOrigin_
          lng = (point.x - origin.x) / self.pixelsPerLonDegree_
          latRadians = (point.y - origin.y) / -self.pixelsPerLonRadian_
          lat = radiansToDegrees(2 * math.atan(math.exp(latRadians)) - math.pi / 2)
          return G_LatLng(lat, lng)

#pixelCoordinate = worldCoordinate * pow(2,zoomLevel)

def getCorners(center, zoom, mapWidth, mapHeight):
    scale = 2**zoom
    proj = MercatorProjection()
    centerPx = proj.fromLatLngToPoint(center)
    SWPoint = G_Point(centerPx.x-(mapWidth/2)/scale, centerPx.y+(mapHeight/2)/scale)
    SWLatLon = proj.fromPointToLatLng(SWPoint)
    NEPoint = G_Point(centerPx.x+(mapWidth/2)/scale, centerPx.y-(mapHeight/2)/scale)
    NELatLon = proj.fromPointToLatLng(NEPoint)
    return {
        'topLat' : NELatLon.lat,
        'rightLon' : NELatLon.lng,
        'bottomLat' : SWLatLon.lat,
        'leftLon' : SWLatLon.lng,
    }

use_mapbox = True
if use_mapbox:
  width = 2560
  height = 2560
else:
  width = 1280
  height = 1280

GOOGLE_KEY = 'AIzaSyB4QxMalieE68zx404oxPZxH3yr9jx85-Y'
MAPBOX_KEY = 'pk.eyJ1IjoiZG1zNDk3IiwiYSI6ImNpajlraDN1czAwMnl0dGtucGxqbmEzZ2sifQ.fblG_9UGH5caOVbKLOD80g'

def center_to_deg(string):
  if string[13] == 'N':
    Nmult = 1
  else:
    Nmult = -1
  degN = Nmult*int(string[0:3])
  minutesN = Nmult*int(string[5:7])
  secondsN = Nmult*float(string[8:12])

  if string[28] == 'E':
    Emult = 1
  else:
    Emult = -1
  degE = Emult*int(string[15:18])
  minutesE = Emult*int(string[20:22])
  secondsE = Emult*float(string[23:27])
  return ((degN + minutesN/60 + secondsN/3600.), (degE + minutesE/60 + secondsE/3600.))

centers = [
  ('Cornell_Campus', {
    'center': '042°26\'54.8"N 076°28\'52.8"W',
    'zoom': 17
    }),
  ('Neno_Airfield', {
    'center': '042°26\'50.3"N 076°36\'45.4"W',
    'zoom': 18
    }),
  ('SFO_Airport', {
    'center': '035°21\'47.7"S 149°09\'54.8"E',
    'zoom': 18
    }),
  ('NAS_Pax', {
    'center': '038°17\'09.0"N 076°24\'36.5"W',
    'zoom': 17
    }),
  ('Game_Farm', {
    'center': '042°26\'36.7"N 076°27\'04.8"W',
    'zoom': 17
    }),
  ('Earth_Center', {
    'center': '000°00\'00.0"N 000°00\'00.0"W',
    'zoom': 16
    })
]

def dictToCenters(d):
  center = center_to_deg(d['center'])
  (lat,lng) = center
  corners = getCorners(G_LatLng(lat, lng), d['zoom'], width, height)
  topLeftCenter = ((corners['topLat'] + center[0])/2,
                   (corners['leftLon'] + center[1])/2)
  bottomLeftCenter = ((corners['bottomLat'] + center[0])/2,
                      (corners['leftLon'] + center[1])/2)
  topRightCenter = ((corners['topLat'] + center[0])/2,
                    (corners['rightLon'] + center[1])/2)
  bottomRightCenter = ((corners['bottomLat'] + center[0])/2,
                       (corners['rightLon'] + center[1])/2)
  centers = (
    ('top_left', topLeftCenter), 
    ('bottom_left', bottomLeftCenter), 
    ('top_right', topRightCenter), 
    ('bottom_right', bottomRightCenter)
  )
  return centers

def centersToRequests(name, d, center_dict):
  fileNames = [];
  for (k, center) in center_dict:
    if use_mapbox:
      req_str = ''.join(('https://api.mapbox.com/v4/mapbox.satellite/', str(center[1]), ',',
                         str(center[0]), ',', str(d['zoom']), '/', str(int(width/2)),
                         'x', str(int(height/2)), '.png?access_token=', MAPBOX_KEY))
    else:
      req_str = ''.join(('https://maps.googleapis.com/maps/api/staticmap?maptype=satellite&center=', 
                         str(center[0]), ',', str(center[1]),'&zoom=', str(d['zoom']),
                         '&size=', str(int(width/2)), 'x', str(int(height/2)), 
                         '&key=', str(GOOGLE_KEY)))
    r = requests.get(req_str)
    if r.status_code == 200:
      fileName = name + '_' + k + '.png'
      fileNames.append(fileName)
      with open (fileName, 'wb') as f:
        f.write(r.content)
  return fileNames

def fileNamesToImage(name, fileNames):
  new_im = Image.new('RGB', (width, height))
  w2 = int(width/2)
  h2 = int(height/2)
  top_left = Image.open(fileNames[0]).resize((w2,h2))
  bottom_left = Image.open(fileNames[1]).resize((w2,h2))
  top_right = Image.open(fileNames[2]).resize((w2,h2))
  bottom_right = Image.open(fileNames[3]).resize((w2,h2))
  for x in fileNames:
    os.remove(x)
  new_im.paste(top_left, (0,0))
  new_im.paste(bottom_left, (0, h2))
  new_im.paste(top_right, (w2, 0))
  new_im.paste(bottom_right, (w2, h2))
  new_im.save(name + '_Satellite.png')

def wrapperFunction(center_dict):
  for (k,v) in center_dict:
    centers = dictToCenters(v)
    fileNames = centersToRequests(k, v, centers)
    fileNamesToImage(k, fileNames)
    (lat,lng) = center_to_deg(v['center'])
    corners = getCorners(G_LatLng(lat, lng), v['zoom'], width, height)
    dim_str = ''.join(('    topLat = ', str(corners['topLat']), ';\n',
                       '    bottomLat = ', str(corners['bottomLat']), ';\n',
                       '    leftLon = ', str(corners['leftLon']), ';\n',
                       '    rightLon = ', str(corners['rightLon']), ';'))
    if k == 'Cornell_Campus':
      print '  if (location === "' + k + '") {'
    else:
      print '  } else if (location === "' + k + '") {'
    print "    imageURL = 'img/satellites/" + k + "_Satellite.png'"
    print dim_str
  print '\n'.join(('  } else {',
    "    imageURL = 'img/plainWhiteSquare.png';",
    "    topLat = 1;",
    "    bottomLat = -1;",
    "    leftLon = 1;",
    "    rightLon = -1;",
    "  }"))

wrapperFunction(centers)