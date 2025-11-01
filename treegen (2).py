"""
Recursive tree drawing program modeled after Dan Garcia's BYOB code
from his course the Beauty and Joy of Computing.
Authors: Adam Moran and Dave Touretzky
Course: 15-294: Rapid Prototyping Technologies

--README--

Usage: 'treegen.py -s [A|B]

treegen.py is a recursive tree drawing program that outputs to both
Tkinter (for previewing) and DXF (for laser cutting).

The program flow is as follows:
1. main() is called to interpret the arguments and call start()
2. start(type) draws the stand base and a vertical branch, and initiates the recursion.
3. branch(l,r) draws the two parallel lines to form a branch, adjusting their
   lengths as needed when used to form a vee shape.
4. vee() recursively calls itself to make a forked branch or call a terminal function.
5. square() is a terminal function that draws a square terminal node.
"""

import math
import random
import getopt,sys
from tkinter import *
from dxfwrite import DXFEngine as dxf

### Initialize Globals ###
(x,y) = (400,600) # Current drawing point
theta = 0        # Current heading
pen = True        # Pen is down (will draw) when True
branch_width = 10 # Must be an even number of pixels
branch_length = 60
branch_angle = 70 # in degrees
dxf_scale = 1 / 3.0   # scale factor to convert pixels to mm
material_thickness = 3.175 # this value in mm
slot_unit = (material_thickness)/dxf_scale # divide out the scale to cancel
stand_unit = slot_unit+(branch_width/2) # varies stand with branch and material
total_objects = 0 # in case we want to count terminal nodes

# This is a hairy computation to make well-formed vee junctions
s = branch_width*math.cos(math.radians(branch_angle/2)) - branch_width/2
mitre_length = s / math.sin(math.radians(branch_angle/2))

### Setup Tkinter ###
master = Tk()
w = Canvas(master, width=1000, height=900)

### Setup DXF Outputs ###
drawing = dxf.drawing('output.dxf')
drawing.header['$LUNITS'] = 4   # units in millimeters
drawing.add_layer('LINES')


""" Description: Lifts up the virtual pen that draws the lines
                 in Tkinter or in the DXF.  If the pen is up when you call
                 forward(), nothing will be drawn, however, the global (x,y)
                 will be updated accordingly.
"""
def pen_up():
    global pen
    pen = False


""" Description: Lowers the virtual pen that draws the lines
                 in Tkinter or in the DXF.  If the pen is down when you call
                 forward(), a line will be written to Tkinter and the DXF.
"""
def pen_down():
    global pen
    pen = True


""" Description:  This is a 'turtle graphics' function that advances the
                  turtle in the forward direction.  If the pen is down, it
                  draws a line, both in Tkinter and in the DXF.
    Inputs: dist [int] -> the distance to move forward in pixels
                          (in the direction of the global, theta)
"""
def forward(dist):
    global x, y, dxf_scale
    new_x = x - dist * math.sin(math.radians(theta-90))
    new_y = y - dist * math.cos(math.radians(theta-90))
    if pen:
        w.create_line(int(x), int(y), int(new_x), int(new_y), fill='blue')
        drawing.add(dxf.line((float(x)*dxf_scale, float(y)*dxf_scale),
                             (float(new_x)*dxf_scale, float(new_y)*dxf_scale),
                             color = 5, #blue
                             layer = 'LINES'))
    (x,y) = (new_x, new_y)


""" Description:  This is a 'turtle graphics' function that changes the turtle's
                  current heading, held in the global variable theta.
    Inputs: angle [int] -> a number in degrees that gets added to the global theta
                           to change the current heading.
"""
def turn(angle):
    global theta
    theta += (-1*angle)


""" Description:  This is a helper function that takes an angle you would provide
                  to Tkinter and corrects for the DXF angle system.
                  IMPORTANT: In order for this function to work correctly, you
                             must not change theta in your circle function!
    Inputs: angle [int] -> the angle you passed to Tkinter
"""
def dxf_angle(angle):
    return angle - 2*theta


""" Description:  This 'turtle graphics' function draws two parallel lines in the
                  forward direction to be used for the branch edges.  The mitre
                  values are used to shorten one line so it forms a properly-fitted vee.
    Inputs: left_mitre [int] -> the distance to skip ahead in the left line
            right_mitre [int] -> the distance to skip ahead in the right line
"""
def branch(left_mitre,right_mitre):
    global x, y, theta
    (oldx,oldy,oldtheta) = (x,y,theta)
    # draw the left line
    pen_up()
    turn(-90)
    forward(branch_width/2)
    turn(90)
    forward(left_mitre)
    pen_down()
    forward(branch_length-left_mitre)
    # draw the right line
    (x,y,theta) = (oldx,oldy,oldtheta)
    pen_up()
    turn(90)
    forward(branch_width/2)
    turn(-90)
    forward(right_mitre)
    pen_down()
    forward(branch_length-right_mitre)
    # advance to endpoint
    (x,y,theta) = (oldx,oldy,oldtheta)
    pen_up()
    forward(branch_length)

""" Description: This is the recursive function that either draws a
    terminal node, or a fork with two recursive calls.
"""
def vee():
    choices = (diamond, donut, circle, square, hexagon, vee, vee,vee)
    global x, y, theta
    (oldx,oldy,oldtheta) = (x,y,theta)
    pen_up()
    turn(90)
    forward(branch_width/2)
    turn(-90)
    turn(-(90-branch_angle/2))
    forward(branch_width/2)
    turn(90)
    branch(mitre_length,0)
    random.choice(choices)()
    (x,y,theta) = (oldx,oldy,oldtheta)
    pen_up()
    turn(-90)
    forward(branch_width/2)
    turn(90)
    turn(90-branch_angle/2)
    forward(branch_width/2)
    turn(-90)
    branch(0,mitre_length)
    random.choice(choices)()


""" Description:  This function draws a square at the current global (x,y)
                  position.
"""
def square():
    global total_objects
    total_objects += 1
    pen_up()
    turn(-90)
    forward(branch_width/2)
    pen_down()
    forward(branch_width*2)
    for i in range(3):
        turn(90)
        forward(branch_width*5)
    turn(90)
    forward(branch_width*2)

def donut(color='red'):
    global x, y
    outerRadius = 32
    newx = x + outerRadius*math.cos(math.radians(theta))
    newy = y - outerRadius*math.sin(math.radians(theta))

    branchangle = math.degrees(math.asin(branch_width / (outerRadius * 2)))

    w.create_arc(int(newx-outerRadius), int(newy+outerRadius),
                 int(newx+outerRadius), int(newy-outerRadius),
                 start=theta + 180 + branchangle,
                 extent=360 - branchangle * 2,
                 style=ARC, outline='blue')
    innerRadius = 22
    w.create_arc(int(newx-innerRadius), int(newy+innerRadius),
                 int(newx+innerRadius), int(newy-innerRadius),
                 start=0, extent=359.999, style=ARC, outline=color)
def diamond():
    global total_objects
    total_objects += 1
    pen_up()

    subtract = math.sqrt(2) * branch_width
    side = 5*branch_width
    turn(-90)
    forward(branch_width/2)
    pen_down()
    turn(45)
    forward(side - subtract)
    turn(90)
    forward(side-subtract/2)
    turn(90)
    forward(side-subtract/2)
    turn(90)
    forward(side - subtract)
    pen_up()

def hexagon():
    global total_objects
    total_objects += 1
    pen_up()
    side = 3 * branch_width
    turn(-90)
    forward(branch_width/2)
    pen_down()

    forward(0.5 * side - 0.5 * branch_width)

    for i in range(5):
        turn(60)
        forward(side)

    turn(60)
    forward(0.5 * side - 0.5*branch_width)

def circle():
    global x, y
    Radius = 32
    newx = x + Radius*math.cos(math.radians(theta))
    newy = y - Radius*math.sin(math.radians(theta))

    branchangle = math.degrees(math.asin(branch_width / (Radius * 2)))
    w.create_arc(int(newx-Radius), int(newy+Radius),
                 int(newx+Radius), int(newy-Radius),
                 start=theta + 180 + branchangle,
                 extent=360 - branchangle * 2,
                 style=ARC, outline='blue')

""" Description:  This function draws one of the 2 base stand types.
    Inputs: standtype [string] -> possibilities are 'A' or 'B'.
"""
def drawbase(standtype):
    print(" -> Drawing base " + standtype)
    if standtype == "A":
        pen_down()
        turn(-180)
        forward(stand_unit*9 + slot_unit)
        turn(-90)
        forward(stand_unit*3)
        turn(90)
        forward(stand_unit*5)
        turn(-90)
        forward(stand_unit*2)
        turn(-90)
        forward(stand_unit*8)
        turn(-90)
        forward(stand_unit*3)
        turn(90)
        forward(slot_unit)
        turn(90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*6)
        forward(branch_width)
        forward(stand_unit*6)
        turn(-90)
        forward(stand_unit*3)
        turn(90)
        forward(slot_unit)
        turn(90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*8)
        turn(-90)
        forward(stand_unit*2)
        turn(-90)
        forward(stand_unit*5)
        turn(90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*9 + slot_unit)
        pen_up()
        forward(branch_width/2)
        turn(90)
    else:
        pen_down()
        turn(-180)
        forward(stand_unit*6)
        turn(-90)
        forward(stand_unit*3)
        turn(90)
        forward(slot_unit)
        turn(90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*3)
        turn(90)
        forward(stand_unit*5)
        turn(-90)
        forward(stand_unit*2)
        turn(-90)
        forward(stand_unit*14)
        forward(branch_width + 2*slot_unit)
        forward(stand_unit*14)
        turn(-90)
        forward(stand_unit*2)
        turn(-90)
        forward(stand_unit*5)
        turn(90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*3)
        turn(90)
        forward(slot_unit)
        turn(90)
        forward(stand_unit*3)
        turn(-90)
        forward(stand_unit*6)
        pen_up()
        forward(branch_width/2)
        turn(90)



""" Description:  The start function draws the stand type specified in the argument
                  to the python call, then draws a vertical branch, and then starts
                  the recursion.
    Inputs: standtype [string] -> possibilities are 'A' or 'B'.
"""
def start(standtype):
    drawbase(standtype)
    branch(0,0)
    vee()


def main(argv):
    standtype = 'A'
    try:
        opts, args = getopt.getopt(argv,"hs:",["standtype="])
    except getopt.GetoptError:
        print('Usage: treegen.py -s [A|B]')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Usage: treegen.py -s [A|B]')
            sys.exit()
        elif opt in ("-s", "--standtype"):
            if arg != "A" and arg != "B":
                print('Standtype must be "A" or "B"')
                sys.exit(2)
            else:
                standtype = arg

    print(' -> Making a tree with stand type ' + standtype)
    w.pack()
    start(standtype)



if __name__ == "__main__":
    main(sys.argv[1:])
    drawing.save()
    print(' -> A DXF file output.dxf was placed in the current directory.')
    print(' -> Starting Tkinter preview')
    mainloop()
