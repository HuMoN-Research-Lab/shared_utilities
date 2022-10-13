import os
import moviepy.editor as mp
import librosa
from glob import glob
from matplotlib import pyplot as plt
import numpy as np
from scipy import signal
from pathlib import Path

def get_clip_list(base_path, file_type):
    '''Return a list of all video files in the base_path folder that match the given file type.'''

    # change directory to folder containing synced videos
    os.chdir(base_path / "SyncedVideos")

    # create general search from file type to use in glob search, including cases for upper and lowercase file types
    file_extension_upper = '*' + file_type.upper()
    file_extension_lower = '*' + file_type.lower()

    # make list of all files with file type
    clip_list = glob(file_extension_upper) + glob(file_extension_lower) #if two capitalization standards are used, the videos may not be in original order
    
    # because glob behaves differently on windows vs. mac/linux, we collect all files both upper and lowercase, and remove redundant files that appear on windows
    unique_clip_list = []
    [unique_clip_list.append(clip) for clip in clip_list if clip not in unique_clip_list]
    print(unique_clip_list)
    
    os.chdir(base_path)
    return unique_clip_list

def get_files(base_path, clip_list):
    '''Get video files from clip_list and store them in a list.
    Return a list of lists containing the video file name and file.
    '''

    # create empty list for storing video files, will contain sublists formatted like [video_file_name,video_file] 
    file_list = []

    video_path = base_path / "SyncedVideos"

    # iterate through clip_list, open video files and store in file_list
    for clip in clip_list:
        # take vid_name and change extension to create audio file name
        vid_name = clip

        # open video files
        video_file = mp.VideoFileClip(os.path.join(video_path,vid_name), audio=True)

        # add name and file to file list
        file_list.append([vid_name, video_file])
        

    return file_list

def get_durations(file_list):
    '''Get video duration from list containing video file name and file.
    Return a list of video file name and durations'''

    # create empty list for storing video durations, will contain sublists formatted like [video_file_name,video_duration] 
    name_duration_list = []
    # iterate through file_list, open video files and store duration in name_duration_list
    for filename_file in file_list:
        file_name = filename_file[0] #f file name
        duration = filename_file[1].duration # file duration

        this_vid_name_duration = [file_name, duration]
        print(this_vid_name_duration)

        # add file name and duration to name duration list
        name_duration_list.append(this_vid_name_duration)

    return name_duration_list

def check_durations(duration_list):
    '''Check if video durations are equal, throw an exception if not (or if no durations are given).'''
    duration_list_without_names = [list_item[1] for list_item in duration_list]

    if len(duration_list_without_names) == 0:
        raise Exception("No durations given")
    else:
        if duration_list_without_names.count(duration_list_without_names[1]) == len(duration_list_without_names):
            print("all rates are equal to", duration_list_without_names[1])
            return duration_list_without_names[1]
        else:
            raise Exception(f"durations are not equal, durations are {duration_list_without_names}")

# set data paths
fmc_data_path = Path("/Users/Philip/Documents/Humon Research Lab/Freemocap_Data/")
sessionID = "partial_charuco_test_7_27_22"

fmc_session_path = fmc_data_path / sessionID

# get list of clips in SyncedVideos folder
clip_list = get_clip_list(fmc_session_path, "MP4")

# get files for each video in clip list
clip_files = get_files(fmc_session_path, clip_list)

# find duration of each video file
duration_list = get_durations(clip_files)

# check if all durations are equal
duration = check_durations(duration_list)
