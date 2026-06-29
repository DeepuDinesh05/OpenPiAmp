import os
import glob

import pygame

from config import *

def scan(folder, state):
    extensions = SUPPORTED_EXTENSIONS
    files = []
    
    for ext in extensions:
        folder_pattern = os.path.join(folder,ext)
        # return all files for each support extension
        files += glob.glob(folder_pattern)

    tracks = sorted(files)
    
    # set state to first clip
    state['track_idx']   = 0
    state['track_count'] = len(tracks)
    state['track_name']  = os.path.splitext(os.path.basename(tracks[0]))[0]
    state['pos_s']       = 0.0
    pygame.mixer.music.load(tracks[0])
    pygame.mixer.music.play()
    state['is_playing']  = True

    return tracks


# load an actual track
def load_track(tracks, state, current_track_index):
    state['track_idx']   = current_track_index
    state['track_count'] = len(tracks)
    state['track_name']  = os.path.splitext(os.path.basename(tracks[current_track_index]))[0]
    state['pos_s']       = 0.0
    pygame.mixer.music.load(tracks[current_track_index])
    pygame.mixer.music.play()
    state['is_playing']  = True
        
