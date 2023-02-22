from trajectory import Trajectory
import math

def test_trajectory():
    traj = Trajectory()

    with open('Camera_point.txt') as f:
        array = []
        count = 0
        for line in f: # read rest of lines
            array.append([float(x) for x in line.split()])
            new_array = array[0]
            new_array[0] = -new_array[0]
            new_array[1] = -new_array[1]
            new_array[2] = -new_array[2]
            traj.add_point(count, new_array[:3], [0,0,0])
            array = []
            count+=1
        traj.interpolate(200)
        return traj
    return None

    # traj = Trajectory()

    # traj.add_point(0, [0.01697442/4, -0.00520116/4, 0.10529092], [0,0,0])
    # traj.add_point(1, [0.01697442/3, -0.00520116/3, 0.10529092 * 1.1], [0,0,0])
    # traj.add_point(2, [0.01697442/2, -0.00520116/2, 0.10529092 * 1.3], [0,0,0])
    # traj.add_point(3, [0.01697442, -0.00520116, 0.10529092], [0,0,0])

    # traj.interpolate(200)