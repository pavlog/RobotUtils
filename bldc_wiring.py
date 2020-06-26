import math 

file = open("test.gcode","w") 
  
file.write("G92 X0 Y0 Z0 E0\n")
file.write("G90\n") 
file.write("M85 600\n") 



cartesianCode = 0
numStatorPoles = 12
RotFeed = 1

extrudeFake = 0

def toXYZ(x,z,angle):
  if cartesianCode:
    global extrudeFake
    extrudeFake=extrudeFake+1
    file.write("G1 ") 
    if x!=None and angle!=None:
      file.write(" X{}".format(x*math.cos(math.radians(angle))))
    if angle!=None:
      yy = x*math.sin(math.radians(angle))
      file.write(" Y{}".format(yy))
    if z!=None:
      file.write(" Z{}".format(z))
    if angle!=None:
      file.write(" E{}.{}".format(extrudeFake,int(angle*100)))
    file.write("\n")
  else:
    file.write("G1 ") 
    if x!=None:
      file.write(" X{}".format(x))
    file.write(" Y{}".format(0))
    if z!=None:
      file.write(" Z{}".format(z))
    if angle!=None:
      file.write(" E{}".format(angle/360.0))
    file.write("\n")


#toXYZ(0,0,0);


z = 0
zUpDelta = 16
xLen = 9
xStart = 0 if cartesianCode==0 else 10
xIncr = 0.35
xRotCompensation = 0.2

file.write("G1 F500\n") 

wiringType = 0

if wiringType==0:
  # total 
  numTurnsValue = 23
  numTurnsPerLayer = [ 
    {"numTurns":numTurnsValue, "xStart":xStart, "xIncr":xIncr, "xRotCompensation":xRotCompensation },
    {"numTurns":numTurnsValue, "xStart":xStart+numTurnsValue*xIncr, "xIncr":-xIncr,"xRotCompensation":-xRotCompensation },
    {"numTurns":numTurnsValue, "xStart":xStart, "xIncr":xIncr,"xRotCompensation":xRotCompensation },
    {"numTurns":4, "xStart":xStart+numTurnsValue*xIncr-2*xIncr, "xIncr":-xIncr*2,"xRotCompensation":-xRotCompensation },
    {"numTurns":4, "xStart":xStart+numTurnsValue*xIncr-4*2*xIncr, "xIncr":xIncr*2,"xRotCompensation":xRotCompensation },
    {"numTurns":numTurnsValue-10, "xStart":xStart+numTurnsValue*xIncr, "xIncr":-xIncr,"xRotCompensation":-xRotCompensation },
    #{"numTurns":numTurnsValue, "xStart":xStartr, "xIncr":xIncr },
    #{"numTurns":numTurnsValue/2, "xStart":xStart+numTurnsValue*xIncr, "xIncr":-xIncr },
    ]
else:
  # test
  numTurnsPerLayer = [ 
    {"numTurns":2, "xStart":xStart, "xIncr":3,"xRotCompensation":xRotCompensation  },
    {"numTurns":2, "xStart":xStart+5, "xIncr":-3,"xRotCompensation":xRotCompensation  },
    ]

count = 0
for turns in numTurnsPerLayer:
  numTurns = turns["numTurns"]
  count+=numTurns

print("NumTurns: ",count)


def CW(pole):
  file.write(";CW\n") 
  curAngle = 360/numStatorPoles*pole
  nextAngle = 360/numStatorPoles*(pole+1)
  for turns in numTurnsPerLayer:
    numTurns = turns["numTurns"]
    xCurStart = turns["xStart"]
    xCurIncr = turns["xIncr"]
    xCurRotComp = turns["xRotCompensation"]
    for turn in range(numTurns):
      toXYZ(xCurStart+xCurIncr*turn,z,curAngle)
      toXYZ(xCurStart+xCurIncr*turn,z+zUpDelta,curAngle)
      toXYZ(xCurStart+xCurIncr*turn+xCurRotComp,z+zUpDelta,nextAngle)
      if turn==numTurns-1:
        toXYZ(xCurStart+xCurIncr*(turn)+xCurRotComp,z,nextAngle)
      else:
        toXYZ(xCurStart+xCurIncr*(turn)+xCurRotComp,z,nextAngle)

#  toXYZ(xStart,z,curAngle)
#  toXYZ(xStart,z+zUpDelta,curAngle)
#  toXYZ(xStart,z+zUpDelta,nextAngle)

def CCW(pole):
  file.write(";CCW\n") 
  curAngle = 360/numStatorPoles*pole
  nextAngle = 360/numStatorPoles*(pole+1)
  for turns in numTurnsPerLayer:
    numTurns = turns["numTurns"]
    xCurStart = turns["xStart"]
    xCurIncr = turns["xIncr"]
    xCurRotComp = turns["xRotCompensation"]
    for turn in range(numTurns):
      toXYZ(xCurStart+xCurIncr*turn,z,nextAngle)
      toXYZ(xCurStart+xCurIncr*turn,z+zUpDelta,nextAngle)
      toXYZ(xCurStart+xCurIncr*turn+xCurRotComp,z+zUpDelta,curAngle)
      if turn==numTurns-1:
        toXYZ(xCurStart+xCurIncr*(turn)+xCurRotComp,z,curAngle)
      else:
        toXYZ(xCurStart+xCurIncr*(turn)+xCurRotComp,z,curAngle)


# note poles index here starts from 1
wiringDiagramm = [
#  {"Order":"CW","Pole":1},
  {"Order":"CCW","Pole":1},
  {"Order":"CW","Pole":2},
  {"Order":"CCW","Pole":3},
  {"Order":"NONE","Pole":9},
  {"Order":"CCW","Pole":9},
  {"Order":"CW","Pole":8},
  {"Order":"CCW","Pole":7},
  ]

for pole in wiringDiagramm:
  file.write((";LAYER:{}\n") .format(pole))
  poleIndex = pole["Pole"]-1
  order = pole["Order"]
  if order=="CW":
    CW(poleIndex)
  elif order=="CCW":
    CCW(poleIndex)
  else:
    curAngle = 360/numStatorPoles*poleIndex
    toXYZ(9,z,None)
    toXYZ(9,z,curAngle)
    toXYZ(0,z,curAngle)

toXYZ(0,z,None)

file.close() #to change file access modes 