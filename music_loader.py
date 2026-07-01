import os
import glob
import pygame
import mutagen

from config import *

def scan(folder, state):
    extensions = SUPPORTED_EXTENSIONS
    files = []

    for ext in extensions:
        folder_pattern = os.path.join(folder,ext)
        # return all files for each support extension
        files += glob.glob(folder_pattern)

    tracks = sorted(files)

    if not tracks:
        state['track_idx']   = 0
        state['track_name']  = "No tracks found"
        state['cover_art']   = None
        state['dur']         = 0.0
        state['pos_s']       = 0.0
        state['is_playing']  = False
        return tracks

    load_track(tracks, state, 0)
    return tracks


# load an actual track
def load_track(tracks, state, current_track_index):
    if not tracks:
        return

    track_metadata = get_metadata(tracks[current_track_index])
    state['track_idx']   = current_track_index
    # fallback to filename if track name doesnt exist
    state['track_name']  = track_metadata.get('title') or os.path.splitext(os.path.basename(tracks[current_track_index]))[0]
    state['cover_art']   = track_metadata.get('image_data')
    state['dur']         = track_metadata.get('duration') or 0.0
    state['pos_s']       = 0.0
    pygame.mixer.music.load(tracks[current_track_index])
    pygame.mixer.music.play()
    state['is_playing']  = True

# next track helper
def next_track(tracks, state):
    if not tracks:
        return

    # if repeat
    if state.get('repeat'):
        load_track(tracks, state, state['track_idx'])
    # if shuffle
    elif state.get('shuffle'):
        import random
        load_track(tracks, state, random.randint(0, len(tracks) - 1))
    # default behavior, auto advance
    else:
        # current state + 1 % (modulus) length of tracks = 0 if last track
        # next_idx = 0 if at last track and button input
        load_track(tracks, state, (state['track_idx'] + 1) % len(tracks))

# prev track helper
def prev_track(tracks, state):
    if not tracks:
        return

    # if shuffle
    if state.get('shuffle'):
        import random
        load_track(tracks, state, random.randint(0, len(tracks) - 1))
    else:
        # current state - 1 % (modulus) length of tracks = last track index if at first track
        # prev_idx = last track index if at first track and button input        
        load_track(tracks, state, (state['track_idx'] - 1) % len(tracks))
      
# returns a dict of string title and an array of raw image data
def get_metadata(filepath):
    metadata = {'title': '', 'image_data': None, 'duration': 0.0}

    try:
        clip = mutagen.File(filepath)

        if clip is None:
            return metadata

        # Duration in seconds
        if clip.info is not None:
            metadata['duration'] = clip.info.length

        # Title extraction
        if 'TIT2' in clip:
            metadata['title'] = str(clip['TIT2'])        # MP3 ID3
        elif 'title' in clip:
            metadata['title'] = clip['title'][0]         # FLAC / OGG / MP4

        # Cover art extraction
        for tag in clip.tags.values():
            if tag.__class__.__name__ == 'APIC':
                metadata['image_data'] = tag.data        # MP3 cover art

        if hasattr(clip, 'pictures') and clip.pictures:
            metadata['image_data'] = clip.pictures[0].data  # FLAC / OGG cover art
        
    except Exception:
        pass
    
    return metadata
            