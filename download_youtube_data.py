import os
import subprocess
import argparse
from pydub import AudioSegment

from pytube import YouTube
from pytube import Playlist
from pytube.exceptions import VideoUnavailable
from pytube.exceptions import RegexMatchError 

from utils import *
from config import *

import time
import math
import xml.etree.ElementTree as ElementTree
from html import unescape


def generate_srt_captions(cap) -> str:
    """Generate "SubRip Subtitle" captions.
    Takes the xml captions from :meth:`~pytube.Caption.xml_captions` and
    recompiles them into the "SubRip Subtitle" format.
    """
    return xml_caption_to_srt(cap)

def xml_caption_to_srt(xml_captions: str) -> str:
    """Convert xml caption tracks to "SubRip Subtitle (srt)".
    :param str xml_captions:
        XML formatted caption tracks.
    """
    segments = []
    root = ElementTree.fromstring(xml_captions)
    for i, child in enumerate(list(root.findall('body/p'))):
        text = ''.join(child.itertext()).strip()
        if not text:
            continue
        caption = unescape(text.replace("\n", " ").replace("  ", " "),)
        try:
            duration = float(child.attrib["d"])
        except KeyError:
            duration = 0.0
        start = float(child.attrib["t"])
        end = start + duration
        sequence_number = i + 1  # convert from 0-indexed to 1.
        line = "{seq}\n{start} --> {end}\n{text}\n".format(
            seq=sequence_number,
            start=float_to_srt_time_format(start),
            end=float_to_srt_time_format(end),
            text=caption,
        )
        segments.append(line)
    return "\n".join(segments).strip()

def float_to_srt_time_format(d: float) -> str:
    """Convert decimal durations into proper srt format.
    :rtype: str
    :returns:
        SubRip Subtitle (str) formatted time duration.
    float_to_srt_time_format(3.89) -> '00:00:03,890'
    """
    fraction, whole = math.modf(d/1000)
    time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
    ms = f"{fraction:.3f}".replace("0.", "")
    return time_fmt + ms



class Youtube:
    def __init__(self, url_video):
        '''
        Args:
            url_video - url video to download
        '''
        self.url_video = url_video
        
    def font_remove(self, data):
        '''
        Remove font tags from text data
        Args:
            data - text data to edit
        '''
        while True:
            beg = data.find('<font color')
            end = data.find('>', beg)
            if beg == -1 or end == -1:
                break
            data = data.replace(data[beg:end + 1], '')

        while True:
            beg = data.find('</')
            end = data.find('>', beg)
            if beg == -1 or end == -1:
                break
            data = data.replace(data[beg:end + 1], '')
        return data

    def get_audio_from_video(self, pth_video):
        '''
        Get and save audio stream from saved video
        Args:
            pth_video - path of saved video
        '''
        pth_audio = pth_video.replace('_video', '', 1)

        command = "ffmpeg -i %s -vn -acodec copy %s" %(pth_video, pth_audio)
        if subprocess.call(command, shell=True) == 0:
            os.remove(pth_video)
            print('Get audio from video to', pth_audio)
        else:
            print('Error with getting audio')

    def download_video(self, data_dir, sub_code='en'):
        '''
        Download video
        Args:
            url_video - url video in Youtube
            data_dir - path to save video
        '''

        #Get id of video at url of video
        id_video = self.url_video.replace('https://www.youtube.com/watch?v=', '')   

        #Check if video files exists
        if os.path.exists(data_dir + id_video + '.mp4') and os.path.exists(data_dir + id_video + '.txt'):
            print(id_video, 'already exists')
            return

        #Get video from Youtube
        video = YouTube(self.url_video)

        #Get russian subtittles if it exists
        cap = video.captions.get_by_language_code(sub_code)
        if cap is None:  
            print('Not subs')        
            return

        #Get audio stream from video and save to file
        streams = video.streams.filter(only_audio=True).all()
        if len(streams)==0:
            print('Not audio stream')
            pth_video = video.streams.filter(subtype='mp4').all()[0].download(data_dir, filename = id_video + '_video')
            print('Video downloaded to', pth_video)
            self.get_audio_from_video(pth_video)
        else:
            streams[0].download(data_dir, filename = id_video + '.mp4')    

        sound = AudioSegment.from_file(data_dir + id_video + '.mp4', 'mp4')
        sound.export(data_dir + id_video + '.wav', format="wav")
        print('Audio downloaded')

        #Save subtitles of video to text file
        sub = generate_srt_captions(cap.xml_captions) 
        sub = self.font_remove(sub) 
        with open(data_dir + id_video + '.txt', 'w', encoding='utf-8') as outfile:
            outfile.write(sub)
            outfile.close()
        print('Subs downloaded')

        return id_video