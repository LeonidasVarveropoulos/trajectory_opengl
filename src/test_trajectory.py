from trajectory import Trajectory
import math
import numpy as np

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
            print(new_array)
            print(output_npc(new_array))
            traj.add_point(count, new_array[:3], [0,0,0])
            array = []
            count+=1
            print("__________")
        traj.interpolate(200)
        return traj
    return None

def output_npc(arr):
    in_array = np.matrix([[arr[0]], [arr[1]], [arr[2]], [1]])

    fx = 1745.417743800858
    fy = 1744.804342507085
    x0 = 1029.543761373819
    y0 = 653.2514270158324
    far = 0.5
    near = 0.001
    cols = 1920#current_image.shape[1]
    rows = 1080#current_image.shape[0]

    perspective = np.matrix([[(-2.0*fx/cols), 0, (cols-2*x0)/cols, 0],
                            [0, 2.0*fy/rows, -(rows-2*y0)/rows, 0],
                            [0, 0, (-far-near)/(far-near), (-2.0 * far * near)/(far-near)],
                            [0, 0, -1, 0]])
    
    out = perspective * in_array
    out/=out[3]
    return out
    
    # traj = Trajectory()

    # traj.add_point(0, [0.01697442/4, -0.00520116/4, 0.10529092], [0,0,0])
    # traj.add_point(1, [0.01697442/3, -0.00520116/3, 0.10529092 * 1.1], [0,0,0])
    # traj.add_point(2, [0.01697442/2, -0.00520116/2, 0.10529092 * 1.3], [0,0,0])
    # traj.add_point(3, [0.01697442, -0.00520116, 0.10529092], [0,0,0])

    # traj.interpolate(200)