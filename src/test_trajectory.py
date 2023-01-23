from trajectory import Trajectory
import math

def test_trajectory():
    traj = Trajectory()

    points = 10
    count = 0

    while (count <= points):
        lin = [math.cos(count), count/points, math.sin(count)]
        ang = [0,0,0]
        traj.add_point(count, lin, ang)

        count+=1

    traj.interpolate(100)
    return traj