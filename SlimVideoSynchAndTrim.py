import os
import sys
import librosa
import time
import moviepy.editor as mp
import numpy as np
from glob import glob
from scipy import signal
from pathlib import Path

class VideoSynchTrimming:
    '''Class of functions for time synchronizing and trimming video files based on cross correlaiton of their audio.'''
    
    def __init__(self):
        '''Initialize VideoSynchTrimmingClass'''
        pass

    def get_clip_list(self, base_path, file_type):
        '''Return a list of all video files in the base_path folder that match the given file type.'''

        # change directory to folder containing raw videos
        os.chdir(base_path / "RawVideos")

        # create general search from file type to use in glob search, including cases for upper and lowercase file types
        file_extension_upper = '*' + file_type.upper()
        file_extension_lower = '*' + file_type.lower()
    
        # make list of all files with file type
        clip_list = glob(file_extension_upper) + glob(file_extension_lower) #if two capitalization standards are used, the videos may not be in original order
        
        # because glob behaves differently on windows vs. mac/linux, we collect all files both upper and lowercase, and remove redundant files that appear on windows
        unique_clip_list = []
        [unique_clip_list.append(clip) for clip in clip_list if clip not in unique_clip_list]
        
        os.chdir(base_path)
        return unique_clip_list

    def get_files(self, base_path, clip_list):
        '''Get video files from clip_list, extract the audio, and put the video and audio files in a list.
        Return a list of lists containing the video file name and file, and audio name and file.
        Also return a list containing the audio sample rate from each file.'''
    
        # create empty list for storing audio and video files, will contain sublists formatted like [video_file_name,video_file,audio_file_name,audio_file] 
        file_list = []

        # create empty list to hold audio sample rate, so we can verify samplerate is the same across all audio files
        sample_rate_list = []

        video_path = base_path / "RawVideos"

        audio_path = base_path / "AudioFiles"
        os.makedirs(audio_path, exist_ok=True)

        # iterate through clip_list, open video files and audio files, and store in file_list
        for clip in clip_list:
            # take vid_name and change extension to create audio file name
            vid_name = clip
            audio_name = clip.split(".")[0] + '.wav'
            # open video files
            video_file = mp.VideoFileClip(str(video_path / vid_name), audio=True)

            # get length of video clip
            vid_length = video_file.duration

            # create .wav file of clip audio
            video_file.audio.write_audiofile(str(audio_path / audio_name))

            # extract raw audio from Wav file
            audio_signal, audio_rate = librosa.load(audio_path / audio_name, sr = None)
            sample_rate_list.append(audio_rate)

            # save video and audio file names and files in list
            file_list.append([vid_name, video_file, audio_name, audio_signal])

            # print relevant video and audio info
            print("video length:", vid_length, "seconds", "audio sample rate", audio_rate, "Hz")

        return file_list, sample_rate_list

    def get_fps_list(self, file_list):
        '''Retrieve frames per second of each video clip in file_list'''
        return [file[1].fps for file in file_list]

    def check_rates(self, rate_list):
        '''Check if audio sample rates or audio frame rates are equal, throw an exception if not (or if no rates are given).'''
        if len(rate_list) == 0:
            raise Exception("no rates given")
        else:
            if rate_list.count(rate_list[0]) == len(rate_list):
                print("all rates are equal to", rate_list[0])
                return rate_list[0]
            else:
                raise Exception(f"rates are not equal, rates are {rate_list}")

    def normalize_audio(self, audio_file):
        '''Perform z-score normalization on an audio file and return the normalized audio file - this is best practice for correlating.'''
        return ((audio_file - np.mean(audio_file))/np.std(audio_file - np.mean(audio_file)))

    def cross_correlate(self, audio1, audio2):
        '''Take two audio files, sync them using cross correlation, and trim them to the same length.
        Inputs are two WAV files to be synced. Return the lag expressed in terms of the audio sample rate of the clips.
        '''

        # compute cross correlation with scipy correlate function, which gives the correlation of every different lag value
        # mode='full' makes sure every lag value possible between the two signals is used, and method='fft' uses the fast fourier transform to speed the process up 
        corr = signal.correlate(audio1, audio2, mode='full', method='fft')
        # lags gives the amount of time shift used at each index, corresponding to the index of the correlate output list
        lags = signal.correlation_lags(audio1.size, audio2.size, mode="full")
        # lag is the time shift used at the point of maximum correlation - this is the key value used for shifting our audio/video
        lag = lags[np.argmax(corr)]
    
        print("lag:", lag)

        return lag

    def find_lags(self, file_list, sample_rate):
        '''Take a file list containing video and audio files, as well as the sample rate of the audio, cross correlate the audio files, and output a lag list.
        The lag list is normalized so that the lag of the latest video to start in time is 0, and all other lags are positive.
        '''
        
        lag_list = [self.cross_correlate(file_list[0][3],file[3])/sample_rate for file in file_list] # cross correlates all audio to the first audio file in the list
        #also divides by the audio sample rate in order to get the lag in seconds
        

        #now that we have our lag array, we subtract every value in the array from the max value
        #this creates a normalized lag array where the latest video has lag of 0
        #the max value lag represents the latest video - thanks Oliver for figuring this out
        norm_lag_list = [(max(lag_list) - value) for value in lag_list]
        
        print("original lag list: ", lag_list, "normalized lag list: ", norm_lag_list)
        
        return norm_lag_list

    def trim_videos(self, file_list, lag_list, base_path):
        # this takes a list of video files and a list of lags, and shortens the beginning of the video by the lags, and trims the ends so they're all the same length
        
        # create new SyncedVideos folder
        synced_path = base_path / "SyncedVideos"
        os.makedirs(synced_path, exist_ok=True)

        # change directory to SyncedVideos folder
        os.chdir(synced_path)
        
        front_trimmed_videos = []

        # for each video in the list, create a new video trimmed from the begining by the lag value for that video, and add it to the empty list
        for i in range(len(file_list)):
            print(file_list[i][1])
            front_trimmed_video = file_list[i][1].subclip(lag_list[i],file_list[i][1].duration)
            #front_trimmed_video = file_list[i][1].subclip(lag_list[i]) # this is a cleaner way of writing this, but needs testing
            front_trimmed_videos.append([file_list[i][0], front_trimmed_video])
        
        print(front_trimmed_videos)

        # now we find the duration of each video and add it to a list to find the shortest video duration
        min_duration = min([video[1].duration for video in front_trimmed_videos])
        print(f"shortest video is {min_duration}")

        # create list to store names of final videos
        video_names = []
        # trim all videos to length of shortest video, and give it a new name
      
        for video in front_trimmed_videos:
            print(video)
            fully_trimmed_video = video[1].subclip(0,min_duration)
            if video[0].split("_")[0] == "raw":
                video_name = "synced_" + video[0][4:]
            else:
                video_name = "synced_" + video[0]
            video_names.append(video_name) #add new name to list to reference for plotting
            fully_trimmed_video.write_videofile(video_name)
            print(f"Cam name: {video_name}, Video Duration: {fully_trimmed_video.duration}")

        # reset our working directory
        os.chdir(base_path)

        return video_names # return names of new videos to reference for plotting

def main():
    '''Run the functions from the VideoSynchTrimming class to sync all videos with the given file type in the base path folder.
    Takes 2 command line arguments, session ID and folder path, with default arguments to allow paths to be entered manually.
    '''

    # start timer to measure performance
    start_timer = time.time()

    # get arguments from command line
    args = sys.argv[1:]

    #parse arguments from command line, with excepts covering hardcoded default values - maybe get rid of these try/except for final script
    try:
        sessionID = args[0]
    except: 
        sessionID = "partial_charuco_test_7_27_22"
    try:
        fmc_data_path = args[1]
    except: 
        fmc_data_path = Path("/Users/Philip/freemocap_data/")

    base_path = fmc_data_path / sessionID

    # instantiate class
    synch_and_trim = VideoSynchTrimming()
    synch_and_trim # this may be unnecessary?

    # set the base path and file type
    file_type = "MP4"  # should work with or without a period at the front, and in either case
    
    # create list of video clip in base path folder
    clip_list = synch_and_trim.get_clip_list(base_path, file_type)

    # get the files and store in list
    files, sr = synch_and_trim.get_files(base_path, clip_list)

    # find the frames per second of each video
    fps = synch_and_trim.get_fps_list(files)
    
    # check that our frame rates and audio sample rates are all equal
    synch_and_trim.check_rates(fps)
    synch_and_trim.check_rates(sr)
    
    # find the lags
    lag_list = synch_and_trim.find_lags(files, synch_and_trim.check_rates(sr))
    
    # use lags to trim the videos
    trimmed_videos = synch_and_trim.trim_videos(files, lag_list, base_path)

    # end performance timer
    end_timer = time.time()
    
    #calculate and display elapsed processing time
    elapsed_time = end_timer - start_timer
    print("elapsed processing time in seconds:", elapsed_time)


if __name__ == "__main__":
    main()
