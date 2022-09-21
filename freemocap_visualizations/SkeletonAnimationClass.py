import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

from pathlib import Path

class SkeletonAnimation:
    def __init__(self):
        # set session folder path
        self.session_folder_path = Path("/Users/Philip/Documents/Humon Research Lab/Freemocap_Data/philip_session_1_3_31_22")

        # get data path as the mediapipe_skel_fr_mar_xyz_2d.npy file location
        data_arrays_path = self.session_folder_path  / "DataArrays"
        mediapipe_file_name = "mediapipe_origin_aligned_skeleton_3D.npy"
        mediapipe_3d_data_path = data_arrays_path / mediapipe_file_name

        # load in saved mediapipe data
        self.mediapipe_skel_fr_mar_xyz = np.load(str(mediapipe_3d_data_path))

        # define video parameters
        self.number_of_frames = self.mediapipe_skel_fr_mar_xyz.shape[0]
        self.frame_interval = 16.6667 # eventually will get this out of fmc pipeline rather than hardcoding

        self.initialize_figure()
        self.define_skeleton_dict()

        # create spatial variables
        self.get_frame_data(0, self.mediapipe_skel_fr_mar_xyz)
        
        # plot initial joint data
        self.tracked_point_graph = self.ax.scatter(self.single_frame_x_data, self.single_frame_y_data, self.single_frame_z_data, color="salmon") #plots all 33 tracked points from mediapipe

        # plot initial skeleton data
        self.create_initial_skeleton(self.single_frame_x_data, self.single_frame_y_data, self.single_frame_z_data, self.skeleton_connection_dict)

    def initialize_figure(self):
        # set up figure
        self.fig = plt.figure(figsize = (7, 7))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.title = self.ax.set_title('3D Test')
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        # self.ax.set_xticklabels([])
        # self.ax.set_yticklabels([])
        # self.ax.set_zticklabels([])

        # get median position and stddev
        number_of_mediapipe_body_markers = 33
        self.get_median_body_markers(number_of_mediapipe_body_markers)
        self.skel_body_stddev = np.nanstd(self.mediapipe_skel_fr_mar_xyz[:,:number_of_mediapipe_body_markers,:])

        # set how much empty space (in terms of skel_body_stdev) to put around skeleton
        scale_factor = 2

        self.set_ax_limits(scale_factor)

    def get_median_body_markers(self, number_of_body_markers):
        median_body_markers_across_frames = np.nanmedian(self.mediapipe_skel_fr_mar_xyz[:,:number_of_body_markers,:], axis=0)
        median_body_markers_xyz = np.nanmedian(median_body_markers_across_frames, axis=0)

        self.median_body_x = median_body_markers_xyz[0]
        self.median_body_y = median_body_markers_xyz[1]
        self.median_body_z = median_body_markers_xyz[2]

    def set_ax_limits(self, scale_factor):
        # get max and min values for x,y,zlim
        x_min = self.median_body_x - scale_factor*self.skel_body_stddev
        x_max = self.median_body_x + scale_factor*self.skel_body_stddev

        y_min = self.median_body_y - scale_factor*self.skel_body_stddev
        y_max = self.median_body_y + scale_factor*self.skel_body_stddev

        z_min = self.median_body_z - scale_factor*self.skel_body_stddev
        z_max = self.median_body_z + scale_factor*self.skel_body_stddev

        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_zlim(z_min, z_max)

    def define_skeleton_dict(self):
        self.skeleton_connection_dict = {
            "eyes": [8, 6, 5, 4, 0, 1, 2, 3, 7],
            "mouth": [10, 9],
            "torso": [11, 23, 24, 12, 11], #repeated start values to close loop
            "rArm": [12, 14, 16],
            "lArm": [11, 13, 15],
            "rHand": [16, 18, 20, 16, 22], #repeated start values to close loop
            "lHand": [15, 17, 19, 15, 21], #repeated start values to close loop
            "rLeg": [24, 26, 28],
            "lLeg": [23, 25, 27],
            "rFoot": [28, 30, 32, 28], #repeated start values to close loop
            "lFoot": [27, 29, 31, 27], #repeated start values to close loop
        }

    def get_frame_data(self, frame, mediapipe_skel_fr_mar_xyz):
        '''Given a frame number, get 3 arrays containing x, y, z data'''
        self.single_frame_x_data = []
        self.single_frame_y_data = []
        self.single_frame_z_data = []

        for tracked_point in mediapipe_skel_fr_mar_xyz[frame][:33]: #only interested in 33 body points, not hand and face points
            self.single_frame_x_data.append(tracked_point[0]) 
            self.single_frame_y_data.append(tracked_point[1])
            self.single_frame_z_data.append(tracked_point[2])
            

    def body_segment_data(self, x, y, z, segment_key, skeleton_connection_dict):
        '''Creates body segment data for a body segment given by the segment_key, based on the joints given in the skeleton_connection_dict.
        Returns separate XYZ lists in proper format for plotting.
        '''

        x_connections, y_connections, z_connections = [], [], []

        for joint in skeleton_connection_dict[segment_key]:
            x_connections.append(x[joint])
            y_connections.append(y[joint])
            z_connections.append(z[joint])

        return x_connections, y_connections, z_connections

    def create_initial_skeleton(self, x, y, z, skeleton_connection_dict):
        # create eyes
        eyes_x, eyes_y, eyes_z = self.body_segment_data(x, y, z, "eyes", skeleton_connection_dict)
        self.eye_line, = self.ax.plot(eyes_x, eyes_y, eyes_z, color = "cornflowerblue")

        # create mouth
        mouth_x, mouth_y, mouth_z = self.body_segment_data(x, y, z, "mouth", skeleton_connection_dict)
        self.mouth_line, = self.ax.plot(mouth_x, mouth_y, mouth_z, color = "cornflowerblue")

        # create torso
        torso_x, torso_y, torso_z = self.body_segment_data(x, y, z, "torso", skeleton_connection_dict)
        self.torso_line, = self.ax.plot(torso_x, torso_y, torso_z, color = "cornflowerblue")

        # create arms
        rArm_x, rArm_y, rArm_z = self.body_segment_data(x, y, z, "rArm", skeleton_connection_dict)
        self.rArm_line, = self.ax.plot(rArm_x, rArm_y, rArm_z, color = "cornflowerblue")

        lArm_x, lArm_y, lArm_z = self.body_segment_data(x, y, z, "lArm", skeleton_connection_dict)
        self.lArm_line, = self.ax.plot(lArm_x, lArm_y, lArm_z, color = "cornflowerblue")

        # create hands
        rHand_x, rHand_y, rHand_z = self.body_segment_data(x, y, z, "rHand", skeleton_connection_dict)
        self.rHand_line, = self.ax.plot(rHand_x, rHand_y, rHand_z, color = "cornflowerblue")

        lHand_x, lHand_y, lHand_z = self.body_segment_data(x, y, z, "lHand", skeleton_connection_dict)
        self.lHand_line, = self.ax.plot(lHand_x, lHand_y, lHand_z, color = "cornflowerblue")

        # create legs
        rLeg_x, rLeg_y, rLeg_z = self.body_segment_data(x, y, z, "rLeg", skeleton_connection_dict)
        self.rLeg_line, = self.ax.plot(rLeg_x, rLeg_y, rLeg_z, color = "cornflowerblue")

        lLeg_x, lLeg_y, lLeg_z = self.body_segment_data(x, y, z, "lLeg", skeleton_connection_dict)
        self.lLeg_line, = self.ax.plot(lLeg_x, lLeg_y, lLeg_z, color = "cornflowerblue")

        # create feet
        rFoot_x, rFoot_y, rFoot_z = self.body_segment_data(x, y, z, "rFoot", skeleton_connection_dict)
        self.rFoot_line, = self.ax.plot(rFoot_x, rFoot_y, rFoot_z, color = "cornflowerblue")

        lFoot_x, lFoot_y, lFoot_z = self.body_segment_data(x, y, z, "lHand", skeleton_connection_dict)
        self.lFoot_line, = self.ax.plot(lFoot_x, lFoot_y, lFoot_z, color = "cornflowerblue")

    def update_skeleton(self, x, y, z, skeleton_connection_dict):
        # update eyes
        eyes_x, eyes_y, eyes_z = self.body_segment_data(x, y, z, "eyes", skeleton_connection_dict)
        self.eye_line.set_data_3d(eyes_x, eyes_y, eyes_z)

        # update mouth
        mouth_x, mouth_y, mouth_z = self.body_segment_data(x, y, z, "mouth", skeleton_connection_dict)
        self.mouth_line.set_data_3d(mouth_x, mouth_y, mouth_z)

        # update torso
        torso_x, torso_y, torso_z = self.body_segment_data(x, y, z, "torso", skeleton_connection_dict)
        self.torso_line.set_data_3d(torso_x, torso_y, torso_z)

        # update arms
        rArm_x, rArm_y, rArm_z = self.body_segment_data(x, y, z, "rArm", skeleton_connection_dict)
        self.rArm_line.set_data_3d(rArm_x, rArm_y, rArm_z)

        lArm_x, lArm_y, lArm_z = self.body_segment_data(x, y, z, "lArm", skeleton_connection_dict)
        self.lArm_line.set_data_3d(lArm_x, lArm_y, lArm_z)

        # update hands
        rHand_x, rHand_y, rHand_z = self.body_segment_data(x, y, z, "rHand", skeleton_connection_dict)
        self.rHand_line.set_data_3d(rHand_x, rHand_y, rHand_z)

        lHand_x, lHand_y, lHand_z = self.body_segment_data(x, y, z, "lHand", skeleton_connection_dict)
        self.lHand_line.set_data_3d(lHand_x, lHand_y, lHand_z)

        # update legs
        rLeg_x, rLeg_y, rLeg_z = self.body_segment_data(x, y, z, "rLeg", skeleton_connection_dict)
        self.rLeg_line.set_data_3d(rLeg_x, rLeg_y, rLeg_z)

        lLeg_x, lLeg_y, lLeg_z = self.body_segment_data(x, y, z, "lLeg", skeleton_connection_dict)
        self.lLeg_line.set_data_3d(lLeg_x, lLeg_y, lLeg_z)

        # update feet
        rFoot_x, rFoot_y, rFoot_z = self.body_segment_data(x, y, z, "rFoot", skeleton_connection_dict)
        self.rFoot_line.set_data_3d(rFoot_x, rFoot_y, rFoot_z)

        lFoot_x, lFoot_y, lFoot_z = self.body_segment_data(x, y, z, "lFoot", skeleton_connection_dict)
        self.lFoot_line.set_data_3d(lFoot_x, lFoot_y, lFoot_z)



    def animate_frame(self, frame_number, x_limits=None, y_limits=None, z_limits=None, scale_factor=None):
        # set title to frame number
        self.ax.set_title('Frame ' + str(frame_number))

        # update single frame data variables
        self.get_frame_data(frame_number, self.mediapipe_skel_fr_mar_xyz)

        # update tracked point plotting
        self.tracked_point_graph._offsets3d = (self.single_frame_x_data, self.single_frame_y_data, self.single_frame_z_data)

        # update skeleton plotting
        self.update_skeleton(self.single_frame_x_data, self.single_frame_y_data, self.single_frame_z_data, self.skeleton_connection_dict)

    def run_animation(self):
        self.anim = FuncAnimation(self.fig, self.animate_frame, frames=np.arange(0, self.number_of_frames, 1), interval=self.frame_interval, save_count=self.number_of_frames)


def main(display_video_bool, save_video_bool):
    start_timer = time.time()

    skeleton_animation = SkeletonAnimation()
    skeleton_animation.run_animation()

    # display plot if parameter set to true
    if display_video_bool:
        plt.show()

    # save video if parameter set to true
    if save_video_bool:
        animation_path = os.path.join(skeleton_animation.session_folder_path, "simple_skeleton_animation.mp4")
        video_writer = animation.FFMpegWriter(fps=60, bitrate=500)
        skeleton_animation.anim.save(animation_path, writer=video_writer)

    end_timer = time.time()
    time_elapsed = end_timer - start_timer
    print(f"Processing took {time_elapsed:.2f} seconds")

if __name__ == "__main__":
    main(display_video_bool=True, save_video_bool=False) # uncomment to display animation
    # main(display_video_bool=False, save_video_bool=True) # uncomment to save animation