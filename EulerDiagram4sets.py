# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 14:30:25 2017

@author: leblanckh
"""

import pandas as pd
import numpy as np
from scipy import stats
import math
import os
import sys
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
import plotly
import plotly.plotly as py
plotly.tools.set_credentials_file(username='kleblanc5909', api_key='MIzFQggygCgieJcytNTR')
import plotly.graph_objs as go
plt.style.use('ggplot')
dataFolder = "/Users/leblanckh/data"
os.chdir(dataFolder)

#==============================================================================
# make a whole library of small modular functions
# that let you answer given R1, R2, and D what is A
# given R1, R2, and D, what is Beta1 and Beta2 ?
# given R1, R2, and D what is Aisoc1 and Aisoc2 ?
#==============================================================================

#Set up a list of radii, a dictionary of areas of overlap, and a list of Circle names for 
#4 circles based on the actual lab data
Radii = [1.784124,1.381976597885342,2.111004122822376,2.185096861184158]
AreaOverlap = {'AO01':1,'AO12':2,'AO23':7, 'AO03':0}
CircleNames = ['Approach \nIncrease,10', 'Consumption \nIncrease,6', 'Approach \nDecrease,14', 'Consumption \nDecrease,15', 'No Response,15']

def Distance_Circle_Center_to_Chord (RadiusBig,RadiusSmall,CCDist):
    """
    given the radii of the two intersecting circles and the distance between their center points, 
    calculate the distance between the center of the large circle and the chord
    
    inputs: RadiusBig, RadiusSmall, CCDist (D)
    return: CenterChordDistance
    """
    
    CenterChordDist = ( CCDist**2 - RadiusSmall**2 + RadiusBig**2) / (2*CCDist)
    return CenterChordDist
    
def Half_Chord_Length_Cusp_to_Cusp (RadiusBig,RadiusSmall,CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points, 
    calculate half the cord length of the Chord line
    """
    Xsolved = Distance_Circle_Center_to_Chord(RadiusBig, RadiusSmall, CCDist)    
    HalfChordLength = math.sqrt( RadiusBig**2 - Xsolved**2)
    return HalfChordLength
    
def Area_of_Small_Triangle (RadiusBig,RadiusSmall,CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of the triangle from the center point of the small circle to the chord
    """
    Xsolved = Distance_Circle_Center_to_Chord(RadiusBig, RadiusSmall, CCDist)
    Ysolved = Half_Chord_Length_Cusp_to_Cusp(RadiusBig, RadiusSmall, CCDist)
    ASmTri = Ysolved*(CCDist-Xsolved)
    return ASmTri
    
def Area_of_Large_Triangle (RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of the triangle from the center point of the large circle to the chord
    """
    Xsolved = Distance_Circle_Center_to_Chord(RadiusBig, RadiusSmall, CCDist)
    Ysolved = Half_Chord_Length_Cusp_to_Cusp(RadiusBig, RadiusSmall, CCDist)
    ALgTri = Xsolved * Ysolved
    return ALgTri
    
def Angle_of_Small_Triangle(RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the angle of the triangle from the center point of the small circle to the chord
    """
    Xsolved = Distance_Circle_Center_to_Chord(RadiusBig, RadiusSmall, CCDist)
    X2 = CCDist - Xsolved
    ratio = X2/RadiusSmall
    Beta1 = 2*(math.acos(ratio))
    return Beta1
    
def Angle_of_Large_Triangle(RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the angle of the triangle from the center point of the large circle to the chord
    """
    Xsolved = Distance_Circle_Center_to_Chord(RadiusBig, RadiusSmall, CCDist)
    Beta2 = 2*(math.acos(Xsolved/RadiusBig))
    return Beta2
    
def Area_of_Small_Sector (RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of the circle section from the center point of the small circle to the chord
    """
    AngleSm = Angle_of_Small_Triangle(RadiusBig, RadiusSmall, CCDist)
    AreaSmSect = (AngleSm/(2*math.pi))*math.pi*RadiusSmall**2
    return AreaSmSect
    
def Area_of_Large_Sector(RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of the circle section from the center point of the large circle to the chord
    """
    AngleLg = Angle_of_Large_Triangle(RadiusBig, RadiusSmall, CCDist)
    AreaLgSect = (AngleLg/(2*math.pi))*math.pi*RadiusBig**2
    return AreaLgSect
    
def Area_of_Small_Lens(RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of the small lens
    """
    AreaSmSect = Area_of_Small_Sector(RadiusBig, RadiusSmall, CCDist)
    AreaSmTri = Area_of_Small_Triangle(RadiusBig, RadiusSmall, CCDist)
    AreaSmLens = AreaSmSect-AreaSmTri
    return AreaSmLens
    
def Area_of_Large_Lens(RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of the small lens
    """
    AreaLgSect = Area_of_Large_Sector(RadiusBig, RadiusSmall, CCDist)
    AreaLgTri = Area_of_Large_Triangle(RadiusBig, RadiusSmall, CCDist)
    AreaLgLens = AreaLgSect - AreaLgTri
    return AreaLgLens
    
def Area_of_Overlap(RadiusBig, RadiusSmall, CCDist):
    """
    given the radii of the two intersecting circles, the distance between their center points,
    calculate the area of overlap of the two circles
    """
    AreaSmLens = Area_of_Small_Lens(RadiusBig, RadiusSmall, CCDist)
    AreaLgLens = Area_of_Large_Lens(RadiusBig, RadiusSmall, CCDist)
    AreaOverlap = AreaSmLens + AreaLgLens
    return AreaOverlap

def Calculate_Distance_for_Given_Overlap(RadiusBig,RadiusSmall,AOverlap):
    """
    guesses a default center to center distance and calculates the area of overlap given that distance
    then compares the calculated area to the desired area of overlap, and adjusts the distance accordingly
    """
    Tolerance = 0.0001
    Dmin = RadiusBig - RadiusSmall
    Dmax = RadiusBig + RadiusSmall
    if AOverlap <= 0:
        print ("There is no overlap between these circles.")
        Dguess = -1
    elif AOverlap >= math.pi*RadiusSmall**2:
        print("The smaller circle is completely encircled by the larger circle.")
        Dguess = 0
    else:
        Dguess = (Dmax+Dmin)/2
        print ('Dguess',Dguess)
        AOCalc = Area_of_Overlap(RadiusBig,RadiusSmall,Dguess)
        print('AoCalc',AOCalc)
        errorVal = AOverlap - AOCalc
        print('errorVal',errorVal)
        loopCounter = 0
        
        while (abs(errorVal)) > Tolerance:
            loopCounter +=1
            #adjust distance
            if errorVal > 0:
                Dmax = Dguess
                Dguess = (Dguess+Dmin)/2
                AOCalc = Area_of_Overlap(RadiusBig,RadiusSmall,Dguess)
                errorVal = AOverlap - AOCalc
            elif errorVal < 0:
                Dmin = Dguess
                Dguess = (Dmax+Dguess)/2
                AOCalc = Area_of_Overlap(RadiusBig,RadiusSmall,Dguess)
                errorVal = AOverlap - AOCalc
            else:
                return Dguess
    return Dguess

def Calculate_Translation(Bangle,Dist):
    """
    calculate the X and Y coordinates for the new circle center given
    the bearing angle (assuming a due north of 0 degrees) and the center to center distance
    """
    Xnew = Dist*math.sin(Bangle)
    Ynew = Dist*math.cos(Bangle)
    return Xnew,Ynew
    
def Get_New_Center(Xog, Yog, Bangle, Dist):
    Xnew, Ynew = Calculate_Translation(Bangle, Dist)
    Xans = Xog + Xnew
    Yans = Yog + Ynew
    return Xans, Yans
    
def Get_Corners (Xcenter,Ycenter,Radius):
    """
    given the radius and coordinates of the center of the circle, 
    calculcate the coordinates of the lower left and upper right corners of a box that
    inscribes the circle perfectly, such that the length of the sides of the box
    are equal to the diameter of the circle
    
    inputs: Radius of new circle, X and Y coordinates of new center
    return: X and Y coordinates of lower left and upper right corners of the box
    """
    XLL = Xcenter - Radius
    YLL = Ycenter - Radius
    XUR = Xcenter + Radius
    YUR = Ycenter + Radius
    return XLL,YLL,XUR,YUR
    
def Convert_Area_Overlap_Key_to_Radius (dictKey, radiiList):
    """
    using the numerical portion of the dictionary key for the area of overlap, 
    translates this key to the associated circle radii and returns them
    """
    radiusList = []
    for aChar in dictKey:
        if aChar.isdigit() :
            radiusList.append(radiiList[int(aChar)])
    radiusList.sort(reverse=True)
    return radiusList
    
def find_All_Corners_in_Order_single_Overlap(theRadii, distances, bearingAngles):
    """
    Returns a list of all lower left (LL) and upper right (UR) corners for a 
    set of circles based on their radii, distance between centers, and angle
    of bearings.  The first circle in the list of radii is assumed to be positioned
    such that its LL corner is at the origin.  The rest of the circles are assumed
    to be set up in a simple numbered fashion (i.e. 0 overlaps with 1, 1 overlaps
    with 2, etc).
    
    Inputs:
        theRadii - a list of all of the radii of each circle
        distances - a dictionary for the distance between each circle
        bearingAngles = a dictionary for the bearing angles between each circle
    Returns:
        corners - A list of LL and UR pairs for the cartesian coordinates of the
                  inscribing box for each of the circles
    """
    CenterX = []
    CenterY = []
    corners = []
    loopIdx = 0
    for radius in theRadii:
        print ("Current radius is ", radius)
        print ("The loopIdx is ", loopIdx)
        if loopIdx == 0:
            LL0 = (0, 0)
            UR0 = (2*theRadii[0], 2*theRadii[0])
            corners.append([LL0, UR0])
            Center0X, Center0Y = theRadii[0], theRadii[0]
            CenterX.append(Center0X)
            CenterY.append(Center0Y)
        else:
            #construct key
            prevIdx = loopIdx - 1
            curKey = 'AO' + str(prevIdx) + str(loopIdx)
            newCenterX, newCenterY = Get_New_Center(CenterX[prevIdx], CenterY[prevIdx], bearingAngles[curKey], distances[curKey])
            CenterX.append(newCenterX)
            CenterY.append(newCenterY)
            newXLL, newYLL, newXUR, newYUR = Get_Corners(newCenterX, newCenterY, theRadii[loopIdx])
            newCornerLL = (newXLL, newYLL)
            newCornerUR = (newXUR, newYUR)
            corners.append([newCornerLL, newCornerUR])
        loopIdx += 1
            
    return CenterX,CenterY,corners
    
    
    #A list to keep up with which radii still need their corners defined
    #unprocessedRadii = theRadii    
#    everyKey = distances.keys()
#    radiiSets = []
#    radiiReverseDict = {}
#    for aKey in everyKey:
#        newSet = Convert_Area_Overlap_Key_to_Radius(aKey, theRadii)
#        radiiSets.append(newSet)
#        newTuple = tuple(newSet)
#        radiiReverseDict[newTuple] = aKey
#    
#    
#    unprocessedRadii.remove(theRadii)
#    knownRadii = [theRadii]
#    
#    while (len(unprocessedRadii) > 0):
#        #look for keys with known radii
#        for aSet in radiiSets:
#            for known in knownRadii:
#                if known in aSet:
#                    #do all the processing and upkeep
#                    knownIdx = theRadii.index(known)
#                    theTuple = tuple(aSet)
#                    theKey = radiiReverseDict[theTuple]
#                    newCenterX, newCenterY = Get_New_Center()
#                    
#        
#        
#        
#    for aDist in distances
#    
    
RadList1 = Convert_Area_Overlap_Key_to_Radius('AO01', Radii)
print (RadList1)

DistanceAO = {}
OverlapKeys = AreaOverlap.keys()
for aKey in OverlapKeys:
    curAO = AreaOverlap.get(aKey)
    if curAO > 0:
        #need to calc distance between circles based on overlap
        #this process begins by determining how many radii are overlapping
        workingRadii = Convert_Area_Overlap_Key_to_Radius( aKey, Radii)
        numOverlap = len(workingRadii)
        if (numOverlap < 2):
            print ("Error with ", aKey, ", there must be at least 2 radii returned for an Overlap to occur,")
        elif (numOverlap == 2):
            #simple case of exactly 2 overlapping circles!
            currDistance = Calculate_Distance_for_Given_Overlap(workingRadii[0], workingRadii[1], curAO)
            DistanceAO[aKey] = currDistance
        else:
            #too many overlapping circles...
            print ("The number of radii overlapping is too large... ", numOverlap)
            
#Use previously defined Distance function to calculate the distance between circle centerpoints
Dist01 = Calculate_Distance_for_Given_Overlap(Radii[1], Radii[0], AreaOverlap['AO01'])
Dist12 = Calculate_Distance_for_Given_Overlap(Radii[2], Radii[1], AreaOverlap['AO12'])
Dist23 = Calculate_Distance_for_Given_Overlap(Radii[2], Radii[3], AreaOverlap['AO23'])
#Dist03 = Calculate_Distance_for_Given_Overlap(Radii[3], Radii[0], AreaOverlap['AO03'])
print (DistanceAO)
print (Dist01)
print (Dist12)
print (Dist23)
#print (Dist03)

#pick bearing angles to achieve desired figure shape
angle01 = math.pi * 7/6
angle12 = math.pi * 5/6
angle23 = math.pi * 1/2
#angle03 = math.pi * 2/3

theBearings = {'AO01':angle01, 'AO12':angle12, 'AO23':angle23}
#Now get the corners
allCenterXs,allCenterYs,allCornersDataSet01 = find_All_Corners_in_Order_single_Overlap(Radii, DistanceAO, theBearings)

print("Final answer:  ", allCenterXs, allCenterYs, allCornersDataSet01)

fig, ax = plt.subplots()
plt.axes()

circle1 = plt.Circle((allCenterXs[0],allCenterYs[0]),radius = Radii[0], color = 'g', alpha = .3)
circle2 = plt.Circle((allCenterXs[1],allCenterYs[1]),radius = Radii[1], color = 'b', alpha = .3)
circle3 = plt.Circle((allCenterXs[2],allCenterYs[2]),radius = Radii[2], color = 'r', alpha = .3)
circle4 = plt.Circle((allCenterXs[3],allCenterYs[3]),radius = Radii[3], color = 'y', alpha = .3)
circle5 = plt.Circle((6,2),radius = 2.185096861184158, color = 'k', alpha = .3)
plt.gca().add_patch(circle1)
plt.gca().add_patch(circle2)
plt.gca().add_patch(circle3)
plt.gca().add_patch(circle4)
plt.gca().add_patch(circle5)

plt.text(allCenterXs[0], allCenterYs[0],CircleNames[0], horizontalalignment='center', verticalalignment='center',multialignment='center')
plt.text(allCenterXs[1], allCenterYs[1],CircleNames[1], horizontalalignment='center', verticalalignment='center',multialignment='center')
plt.text(allCenterXs[2],allCenterYs[2],CircleNames[2], horizontalalignment='center', verticalalignment='center',multialignment='center')
plt.text(allCenterXs[3],allCenterYs[3],CircleNames[3], horizontalalignment='center', verticalalignment='center',multialignment='center')
plt.text(6,2,CircleNames[4], horizontalalignment='center', verticalalignment='center')
plt.text(1,0.5, AreaOverlap['AO01'], color = 'red')
plt.text(1,-1, AreaOverlap['AO12'], color = 'red')
plt.text(3,-3, AreaOverlap['AO23'], color = 'red')


plt.axis('scaled')
plt.savefig('ConsumptionApproach2.svg',format = "svg", transparent = True)


#trace0 = go.Scatter(
#    x = allCenterXs,
#    y= allCenterYs,
#    text=['$Consumption Increase$', '$Approach Increase$','$Consumption Decrease$','$Approach Decrease$'],
#    mode='text',
#    textfont=dict(
#        color='black',
#        size=18,
#        family='Arial',
#    )
#)
#
#data = [trace0]
#
#layout = {
#    'xaxis': {
#        'showticklabels': False,
#        'autotick': False,
#        'showgrid': False,
#        'zeroline': False,
#    },
#    'yaxis': {
#        'showticklabels': False,
#        'autotick': False,
#        'showgrid': False,
#        'zeroline': False,
#    },
#    'shapes': [
#        {
#            'opacity': 0.3,
#            'xref': 'x',
#            'yref': 'y',
#            'fillcolor': 'brown',
#            'x0': allCornersDataSet01[0][0][0],
#            'y0': allCornersDataSet01[0][0][1],
#            'x1': allCornersDataSet01[0][1][0],
#            'y1': allCornersDataSet01[0][1][1],
#            'type': 'circle',
#            'line': {
#                'color': 'brown',
#            },
#        },
#        {
#            'opacity': 0.3,
#            'xref': 'x',
#            'yref': 'y',
#            'fillcolor': 'green',
#            'x0': allCornersDataSet01[1][0][0],
#            'y0': allCornersDataSet01[1][0][1],
#            'x1': allCornersDataSet01[1][1][0],
#            'y1': allCornersDataSet01[1][1][1],
#            'type': 'circle',
#            'line': {
#                'color': 'green',
#            },
#        },
#        {
#            'opacity': 0.3,
#            'xref': 'x',
#            'yref': 'y',
#            'fillcolor': 'brown',
#            'x0': allCornersDataSet01[2][0][0],
#            'y0': allCornersDataSet01[2][0][1],
#            'x1': allCornersDataSet01[2][1][0],
#            'y1': allCornersDataSet01[2][1][1],
#            'type': 'circle',
#            'line': {
#                'color': 'brown',
#            },
#        },
#        {
#            'opacity': 0.3,
#            'xref': 'x',
#            'yref': 'y',
#            'fillcolor': 'green',
#            'x0': allCornersDataSet01[3][0][0],
#            'y0': allCornersDataSet01[3][0][1],
#            'x1': allCornersDataSet01[3][1][0],
#            'y1': allCornersDataSet01[3][1][1],
#            'type': 'circle',
#            'line': {
#                'color': 'green',
#            },
#        },
#    ],
#    'margin': {
#        'l': 20,
#        'r': 20,
#        'b': 100
#    },
#    'height': 800,
#    'width': 800,
#}
#fig = {
#    'data': data,
#    'layout': layout,
#}
#py.plot(fig, filename='EulerDiagram_ConsumptionApproach')
            
#if DistC2C>= RadSmall+RadLg:
#    print ("There is no overlap between these circles.")
#
#elif DistC2C <= RadLg - RadSmall:
#    print ("The smaller circle is completely encircled by the larger circle. Overlap = ", math.pi*RadSmall**2)
#else:
#        
#    Overlap = Area_of_Overlap(RadLg,RadSmall,DistC2C)
#    CalcDistC2C = Calculate_Distance_for_Given_Overlap(RadLg,RadSmall,AreaOverlap)
#    NewCenterCircle = Get_New_Center(0,0,(3*math.pi)/2,CalcDistC2C)
#
#print(Overlap, CalcDistC2C, NewCenterCircle)
