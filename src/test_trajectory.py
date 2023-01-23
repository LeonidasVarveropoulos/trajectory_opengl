from trajectory import Trajectory
import math

def test_trajectory():
    traj = Trajectory()

    points = 50
    count = 0

    while (count <= points):
        t = count/10.0
        radius = 1.0/4.0
        x = radius*(math.sin(t)+2.0*math.sin(2.0*t))
        y = radius*(math.cos(t)-2.0*math.cos(2.0*t))
        z = radius*(-math.sin(3.0*t))

        lin = [x, y, z]
        ang = [0,0,0]
        traj.add_point(count, lin, ang)

        count+=1

    traj.interpolate(200)
    return traj