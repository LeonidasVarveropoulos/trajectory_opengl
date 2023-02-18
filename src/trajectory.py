from scipy import interpolate
import numpy as np

class Trajectory:

    def __init__(self):
        self.clear()
    
    def add_point(self, time, lin, ang):
        self.time.append(time)

        # Project points here and convert bounds to screen space (-1, 1)
        # TODO

        self.lin_x.append(lin[0])
        self.lin_y.append(lin[1])
        self.lin_z.append(lin[2])

        self.ang_x.append(ang[0])
        self.ang_y.append(ang[1])
        self.ang_z.append(ang[2])

    def clear(self):
        # Time
        self.time = []

        # Linear
        self.lin_x = []
        self.lin_y = []
        self.lin_z = []

        # Angular
        self.ang_x = []
        self.ang_y = []
        self.ang_z = []

    def interpolate(self, num_points):
        min_time = self.time[0]
        max_time = self.time[len(self.time) - 1]

        initial_time = self.time

        # Create a new time array evenly spaced
        self.time = []
        count = 0
        while (count <= num_points):
            self.time.append(min_time + (count * ((max_time - min_time)/num_points)))
            count+=1

        # Lin x interpolation
        self.lin_x_tck = interpolate.splrep(initial_time, self.lin_x)
        self.lin_x = interpolate.splev(self.time, self.lin_x_tck)

        # Lin y interpolation
        self.lin_y_tck = interpolate.splrep(initial_time, self.lin_y)
        self.lin_y = interpolate.splev(self.time, self.lin_y_tck)

        # Lin z interpolation
        self.lin_z_tck = interpolate.splrep(initial_time, self.lin_z)
        self.lin_z = interpolate.splev(self.time, self.lin_z_tck)

        # Ang x interpolation
        self.ang_x_tck = interpolate.splrep(initial_time, self.ang_x)
        self.ang_x = interpolate.splev(self.time, self.ang_x_tck)

        # Ang y interpolation
        self.ang_y_tck = interpolate.splrep(initial_time, self.ang_y)
        self.ang_y = interpolate.splev(self.time, self.ang_y_tck)

        # Ang z interpolation
        self.ang_z_tck = interpolate.splrep(initial_time, self.ang_z)
        self.ang_z = interpolate.splev(self.time, self.ang_z_tck)

    def interpolate_single_pose(self, time_scale):
        time = (self.time[len(self.time) - 1] - self.time[0]) * time_scale

        lin_x = interpolate.splev(time, self.lin_x_tck)
        lin_y = interpolate.splev(time, self.lin_y_tck)
        lin_z = interpolate.splev(time, self.lin_z_tck)

        ang_x = interpolate.splev(time, self.ang_x_tck)
        ang_y = interpolate.splev(time, self.ang_y_tck)
        ang_z = interpolate.splev(time, self.ang_z_tck)

        return [lin_x.item(0), lin_y.item(0), lin_z.item(0), ang_x.item(0), ang_y.item(0), ang_z.item(0)]

    def get_vertices(self):
        vert = []
        
        count = 0
        while (count < len(self.time)):
            # Double up vertices for thick lines
            vert.append(self.lin_x[count])
            vert.append(self.lin_y[count])
            vert.append(self.lin_z[count])

            vert.append(self.lin_x[count])
            vert.append(self.lin_y[count])
            vert.append(self.lin_z[count])

            count+=1

        return np.array(vert, dtype = np.float32)
    
    def get_next_vertices(self):
        vert = []
        
        count = 0
        while (count < len(self.time)):
            # Double up vertices for thick lines
            if (count == len(self.time) - 1):
                vert.append(self.lin_x[count])
                vert.append(self.lin_y[count])
                vert.append(self.lin_z[count])

                vert.append(self.lin_x[count])
                vert.append(self.lin_y[count])
                vert.append(self.lin_z[count])
            else:
                vert.append(self.lin_x[count + 1])
                vert.append(self.lin_y[count + 1])
                vert.append(self.lin_z[count + 1])

                vert.append(self.lin_x[count + 1])
                vert.append(self.lin_y[count + 1])
                vert.append(self.lin_z[count + 1])

            count+=1

        return np.array(vert, dtype = np.float32)
    
    def get_vertices_direction(self):
        vert = []
        
        count = 0
        while (count < len(self.time)):
            # Double up vertices for thick lines
            vert.append(1.0)
            vert.append(-1.0)

            count+=1

        return np.array(vert, dtype = np.float32)
    
    def get_vert_count(self):
        vert = []
        
        count = 0
        while (count < len(self.time)):
            # Double up vertices for thick lines
            vert.append(count)
            vert.append(count)

            count+=1

        return np.array(vert, dtype = np.float32)
    
    def get_orientation_poses(self, pose_number):
        poses = []

        step = int(len(self.ang_x)/pose_number)
        count = 0
        while (count < len(self.ang_x)):
            poses.append([self.lin_x[count], self.lin_y[count], self.lin_z[count], self.ang_x[count], self.ang_y[count], self.ang_z[count]])
            count += step
        return poses
    
    def get_path_timing(self):
        return self.time[0], self.time[len(self.time) - 1]