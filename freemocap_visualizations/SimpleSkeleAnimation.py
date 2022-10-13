import os
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits import mplot3d
from matplotlib.animation import FuncAnimation

from pathlib import Path

###############################################################################################################
###############################################################################################################

def get_frame_data(frame, mediapipe_skel_fr_mar_xyz):
    '''Given a frame number, get 3 arrays containing x, y, z data'''
    single_frame_x_data = []
    single_frame_y_data = []
    single_frame_z_data = []

    for tracked_point in mediapipe_skel_fr_mar_xyz[frame][:33]: #only interested in 33 body points, not hand and face points
        single_frame_x_data.append(tracked_point[0]) 
        single_frame_y_data.append(tracked_point[1])
        single_frame_z_data.append(tracked_point[2])
        
    return single_frame_x_data, single_frame_y_data, single_frame_z_data

def body_segment_data(x, y, z, segment_key, skeleton_connection_dict):
    '''Creates body segment data for a body segment given by the segment_key, based on the joints given in the skeleton_connection_dict.
    Returns separate XYZ lists in proper format for plotting.'''
    x_connections, y_connections, z_connections = [], [], []

    for joint in skeleton_connection_dict[segment_key]:
        x_connections.append(x[joint])
        y_connections.append(y[joint])
        z_connections.append(z[joint])

    return x_connections, y_connections, z_connections


def create_initial_skeleton(x, y, z, skeleton_connection_dict):
    # create eyes
    eyes_x, eyes_y, eyes_z = body_segment_data(x, y, z, "eyes", skeleton_connection_dict)
    eye_line, = ax.plot(eyes_x, eyes_y, eyes_z, color = "cornflowerblue")

    # create mouth
    mouth_x, mouth_y, mouth_z = body_segment_data(x, y, z, "mouth", skeleton_connection_dict)
    mouth_line, = ax.plot(mouth_x, mouth_y, mouth_z, color = "cornflowerblue")

    # create torso
    torso_x, torso_y, torso_z = body_segment_data(x, y, z, "torso", skeleton_connection_dict)
    torso_line, = ax.plot(torso_x, torso_y, torso_z, color = "cornflowerblue")

    # create arms
    rArm_x, rArm_y, rArm_z = body_segment_data(x, y, z, "rArm", skeleton_connection_dict)
    rArm_line, = ax.plot(rArm_x, rArm_y, rArm_z, color = "cornflowerblue")

    lArm_x, lArm_y, lArm_z = body_segment_data(x, y, z, "lArm", skeleton_connection_dict)
    lArm_line, = ax.plot(lArm_x, lArm_y, lArm_z, color = "cornflowerblue")

    # create hands
    rHand_x, rHand_y, rHand_z = body_segment_data(x, y, z, "rHand", skeleton_connection_dict)
    rHand_line, = ax.plot(rHand_x, rHand_y, rHand_z, color = "cornflowerblue")

    lHand_x, lHand_y, lHand_z = body_segment_data(x, y, z, "lHand", skeleton_connection_dict)
    lHand_line, = ax.plot(lHand_x, lHand_y, lHand_z, color = "cornflowerblue")

    # create legs
    rLeg_x, rLeg_y, rLeg_z = body_segment_data(x, y, z, "rLeg", skeleton_connection_dict)
    rLeg_line, = ax.plot(rLeg_x, rLeg_y, rLeg_z, color = "cornflowerblue")

    lLeg_x, lLeg_y, lLeg_z = body_segment_data(x, y, z, "lLeg", skeleton_connection_dict)
    lLeg_line, = ax.plot(lLeg_x, lLeg_y, lLeg_z, color = "cornflowerblue")

    # create feet
    rFoot_x, rFoot_y, rFoot_z = body_segment_data(x, y, z, "rFoot", skeleton_connection_dict)
    rFoot_line, = ax.plot(rFoot_x, rFoot_y, rFoot_z, color = "cornflowerblue")

    lFoot_x, lFoot_y, lFoot_z = body_segment_data(x, y, z, "lHand", skeleton_connection_dict)
    lFoot_line, = ax.plot(lFoot_x, lFoot_y, lFoot_z, color = "cornflowerblue")

    #returning all of these directly seems like an ungodly solution
    # should make an animation class where all of these are set as properties, instead of just returning them...
    return eye_line, mouth_line, torso_line, rArm_line, lArm_line, rHand_line, lHand_line, rLeg_line, lLeg_line, rFoot_line, lFoot_line

def update_skeleton(x, y, z, skeleton_connection_dict, eye_line, mouth_line, torso_line, rArm_line, lArm_line, rHand_line, lHand_line, rLeg_line, lLeg_line, rFoot_line, lFoot_line):
    # update eyes
    eyes_x, eyes_y, eyes_z = body_segment_data(x, y, z, "eyes", skeleton_connection_dict)
    eye_line.set_data_3d(eyes_x, eyes_y, eyes_z)

    # update mouth
    mouth_x, mouth_y, mouth_z = body_segment_data(x, y, z, "mouth", skeleton_connection_dict)
    mouth_line.set_data_3d(mouth_x, mouth_y, mouth_z)

    # update torso
    torso_x, torso_y, torso_z = body_segment_data(x, y, z, "torso", skeleton_connection_dict)
    torso_line.set_data_3d(torso_x, torso_y, torso_z)

    # update arms
    rArm_x, rArm_y, rArm_z = body_segment_data(x, y, z, "rArm", skeleton_connection_dict)
    rArm_line.set_data_3d(rArm_x, rArm_y, rArm_z)

    lArm_x, lArm_y, lArm_z = body_segment_data(x, y, z, "lArm", skeleton_connection_dict)
    lArm_line.set_data_3d(lArm_x, lArm_y, lArm_z)

    # update hands
    rHand_x, rHand_y, rHand_z = body_segment_data(x, y, z, "rHand", skeleton_connection_dict)
    rHand_line.set_data_3d(rHand_x, rHand_y, rHand_z)

    lHand_x, lHand_y, lHand_z = body_segment_data(x, y, z, "lHand", skeleton_connection_dict)
    lHand_line.set_data_3d(lHand_x, lHand_y, lHand_z)

    # update legs
    rLeg_x, rLeg_y, rLeg_z = body_segment_data(x, y, z, "rLeg", skeleton_connection_dict)
    rLeg_line.set_data_3d(rLeg_x, rLeg_y, rLeg_z)

    lLeg_x, lLeg_y, lLeg_z = body_segment_data(x, y, z, "lLeg", skeleton_connection_dict)
    lLeg_line.set_data_3d(lLeg_x, lLeg_y, lLeg_z)

    # update feet
    rFoot_x, rFoot_y, rFoot_z = body_segment_data(x, y, z, "rFoot", skeleton_connection_dict)
    rFoot_line.set_data_3d(rFoot_x, rFoot_y, rFoot_z)

    lFoot_x, lFoot_y, lFoot_z = body_segment_data(x, y, z, "lFoot", skeleton_connection_dict)
    lFoot_line.set_data_3d(lFoot_x, lFoot_y, lFoot_z)

    #would love to do all of this programatically... 


def animate_frame(frame_number, x_limits=None, y_limits=None, z_limits=None, scale_factor=None):
    # set title to frame number
    ax.set_title('Frame ' + str(frame_number))

    # update tracked point variables
    tracked_point_x, tracked_point_y, tracked_point_z = get_frame_data(frame_number, mediapipe_skel_fr_mar_xyz)

    # update tracked point plotting
    tracked_point_graph._offsets3d = (tracked_point_x, tracked_point_y, tracked_point_z)

    # update skeleton plotting
    update_skeleton(tracked_point_x, tracked_point_y, tracked_point_z, skeleton_connection_dict, eye_line, mouth_line, torso_line, rArm_line, lArm_line, rHand_line, lHand_line, rLeg_line, lLeg_line, rFoot_line, lFoot_line)



if __name__ == "__main__":

    # define skeleton connection dictionary
    skeleton_connection_dict = {
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

    # start timer for timing processing
    start_timer = time.time()

    # set video display and save parameters 
    display_video_bool = False #set to True to play video in real time
    save_video_bool = True #set to True to save video to file

    # set session folder path
    session_folder_path = Path("/Users/Philip/Documents/Humon Research Lab/Freemocap_Data/philip_session_1_3_31_22")

    # get data path as the mediapipe_skel_fr_mar_xyz_2d.npy file location
    data_arrays_path = session_folder_path  / "DataArrays"
    mediapipe_file_name = "mediapipe_origin_aligned_skeleton_3D.npy"
    mediapipe_3d_data_path = data_arrays_path / mediapipe_file_name

    # load in saved mediapipe data
    mediapipe_skel_fr_mar_xyz = np.load(str(mediapipe_3d_data_path))

    # define video parameters
    number_of_frames = mediapipe_skel_fr_mar_xyz.shape[0]
    frame_interval = 16.6667

    #! make this "initialize frame" function
    # set up figure
    fig = plt.figure(figsize = (7, 7))
    ax = fig.add_subplot(111, projection='3d')
    title = ax.set_title('3D Test')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    # ax.set_xticklabels([])
    # ax.set_yticklabels([])
    # ax.set_zticklabels([])

    # get median position 
    number_of_mediapipe_body_markers = 33
    median_body_markers_across_frames = np.nanmedian(mediapipe_skel_fr_mar_xyz[:,:number_of_mediapipe_body_markers,:], axis=0)
    median_body_markers_xyz = np.nanmedian(median_body_markers_across_frames, axis=0)

    median_body_x = median_body_markers_xyz[0]
    median_body_y = median_body_markers_xyz[1]
    median_body_z = median_body_markers_xyz[2]
    
    skel_body_stddev = np.nanstd(mediapipe_skel_fr_mar_xyz[:,:number_of_mediapipe_body_markers,:])

    # set how much empty space (in terms of skel_body_stdev) to put around skeleton
    scale_factor = 2
    
    # get max and min values for x,y,zlim
    x_min = median_body_x - scale_factor*skel_body_stddev
    x_max = median_body_x + scale_factor*skel_body_stddev
    
    y_min = median_body_y - scale_factor*skel_body_stddev
    y_max = median_body_y + scale_factor*skel_body_stddev

    z_min = median_body_z - scale_factor*skel_body_stddev
    z_max = median_body_z + scale_factor*skel_body_stddev

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    # create spatial variables
    tracked_point_x, tracked_point_y, tracked_point_z = get_frame_data(0, mediapipe_skel_fr_mar_xyz)
    
    # plot initial joint data
    tracked_point_graph = ax.scatter(tracked_point_x, tracked_point_y, tracked_point_z, color="salmon") #plots all 33 tracked points from mediapipe

    # plot initial skeleton data
    eye_line, mouth_line, torso_line, rArm_line, lArm_line, rHand_line, lHand_line, rLeg_line, lLeg_line, rFoot_line, lFoot_line = create_initial_skeleton(tracked_point_x, tracked_point_y, tracked_point_z, skeleton_connection_dict)

    # run animation
    anim = FuncAnimation(fig, animate_frame, frames=np.arange(0, number_of_frames, 1), interval=frame_interval, save_count=number_of_frames)
    plt.tight_layout()

    # display plot if parameter set to true
    if display_video_bool:
        plt.show()

    # save video if parameter set to true
    if save_video_bool:
        animation_path = os.path.join(session_folder_path, "simple_skeleton_animation.mp4")
        video_writer = animation.FFMpegWriter(fps=60, bitrate=500)
        anim.save(animation_path, writer=video_writer)

    end_timer = time.time()
    time_elapsed = end_timer - start_timer
    print(f"Processing took {time_elapsed} seconds")