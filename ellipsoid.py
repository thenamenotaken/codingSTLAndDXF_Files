#!/usr/bin/env python

import math
import stlwrite as stl

PI = math.pi

def frange(x, maximum, step):
    while x < maximum:
        yield x
        x += step

def get_ellipse(A,B,x0,y0):
    # Return a list of triangular faces for an axis-aligned ellipse
    # Parameters:
    #   A and B are the semi-major and semi-minor axis lengths
    #   x0 and y0 define the center of the list
    faces = []
    center = (x0,y0,0)
    thetaStep = PI/16
    for theta in frange(0, 2*PI, thetaStep):
        p1 = (x0 + A * math.cos(theta), y0 + B * math.sin(theta), 0)
        p2 = (x0 + A * math.cos(theta+thetaStep), y0 + B * math.sin(theta+thetaStep), 0)
        faces.append([center, p1, p2])
    return faces

def get_ellipsoid(A, B, C, x0, y0, z0):
    """""
    Parameters:
        A, B, C: semi-axis lengths (A=x-axis, B=y-axis, C=z-axis)
        x0, y0, z0: center coordinates
        x(theta, phi) = x0 + Acose(theta)cos(phi)
        y(theta, phi) = y0 + Bsin(theta)cos(phi) <-- cos(phi) bc is lattitude so on same line as x
        z(theta, phi) = z0 + Csin(phi) <-- C represents the flattness/roundness of the shape, A=B=C is a perfect
        sphere

    Approach:
        -Create triangle faces, each face being [p1, p2, p3]
        2 Cases:
            1) We create a rectangle where the top line is a different level of phi than the bottom with 4 pts (p1,p2,p3,p4)
            This will create 2 triangles [p1, p2, p3] & [p1, p3, p4]
            2) When we at the north or south pole, all triangles converge into one pt, so @ phi = pi/2 or -pi/2
                -this is basically 2 casses for bottom and top end
    ^this is for my ref when im coding dw about it

    """
    faces = []
    
    theta_step = math.pi / 8    # 16 divisions around a row/ longitude
    phi_step = math.pi / 8      # 16 divisions on a col / lattitude
    
    # this is a helper function to calculate all the pts from earlier with equations from sheet
    def ellipsoid_point(theta, phi):
        x = x0 + A * math.cos(theta) * math.cos(phi)
        y = y0 + B * math.sin(theta) * math.cos(phi)
        z = z0 + C * math.sin(phi)
        
        return (x, y, z)
    
    # phi from -π/2 to +π/2 <-- top to bottom of sphere/oval thingy
    phi_start = -math.pi / 2
    phi_end = math.pi / 2
    
    phi = phi_start
    while (phi < phi_end - phi_step/2):  # /2 is so it don't stop too early, buffer
        phi_next = phi + phi_step
        
        # Case 2.1 (bottom) - phi = -π/2

        if abs(phi_next - phi_start) < 1e-10: #the code tweaks when I say phi_next == phi_start, have to acc for small discrapency
            # cos(phi) = 0
            south_pole = ellipsoid_point(0, phi)

            #create triangles from south pole to first latitude ring - as in first circle from bottom
            theta = 0
            
            while (theta < 2 * math.pi - theta_step/2):
                theta_next = theta + theta_step
                
                p1 = ellipsoid_point(theta, phi_next)
                p2 = ellipsoid_point(theta_next, phi_next)
                
                # Triangle from pt_south_pole -> p1 -> p2 
                faces.append([south_pole, p1, p2])

                theta += theta_step
        
        # Case 2.2 (top) - phi = π/2
        elif abs(phi_next - phi_end) < 1e-10: #for code tweaking again bruhhhhhhhhhhhhhh
            # at north pole, cos(phi) = 0 again
            north_pole = ellipsoid_point(0, phi_next)
            
            #create triangles from last latitude ring to north pole
            theta = 0
            while theta < 2 * math.pi - theta_step/2:
                theta_next = theta + theta_step
                
                p1 = ellipsoid_point(theta, phi)
                p2 = ellipsoid_point(theta_next, phi)
                
                faces.append([p1, p2, north_pole])
                
                theta += theta_step
        
        # Case 1 
        else:
            theta = 0
            while theta < 2 * math.pi - theta_step/2:
                theta_next = theta + theta_step
                
                # Four corners of the rect thingie
                p1 = ellipsoid_point(theta, phi)           # bottomLeft
                p2 = ellipsoid_point(theta_next, phi)      # bottomRight
                p3 = ellipsoid_point(theta_next, phi_next) # topRight
                p4 = ellipsoid_point(theta, phi_next)      # topLeft
                
                # triag1 = p1 -> p2 -> p3
                faces.append([p1, p2, p3])
                # triag2 =  p1 -> p3 -> p4
                faces.append([p1, p3, p4])
                
                theta += theta_step
        
        phi += phi_step
    
    return faces

if __name__ == "__main__":

    triangles = get_ellipsoid(1, 1, 1, 0, 0, 0)
    print(f"Generated {len(triangles)} triangles for a sphere")
    
    filename = 'test_sphere.stl'
    with open(filename, 'wb') as fp:
        writer = stl.ASCII_STL_Writer(fp)
        writer.add_faces(triangles)
        writer.close()
    print('Wrote ' + filename)



