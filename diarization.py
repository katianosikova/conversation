from pyannote.core import Segment, notebook

import torch
import os

from utils import *
from config import *

class Diarization:
    def __init__(self, id_video):
        self.id_video = id_video
        
    def get_diar(self):
        crop_video_dir = crop_data_dir + self.id_video + '/'
        filename_list = os.listdir(crop_video_dir)
        for file_name in filename_list:
            self.get_snippet_diar(file_name)
        
    def get_snippet_diar(self, file_name):
        file_name_path = crop_data_dir + self.id_video + '/' + file_name
        
        audio = {'uri': file_name.replace('.wav', ''),'audio': file_name_path}
        notebook.reset()

        pipeline = torch.hub.load('pyannote/pyannote-audio', 'dia')
        diarization = pipeline(audio)
        rttm_video_dir = rttm_dir + self.id_video + '/'
        with open(rttm_video_dir + file_name.replace('.wav', '.rttm'), 'w') as f:
            diarization.write_rttm(f)