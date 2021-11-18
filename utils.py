import requests, datetime, time, re, os
from bs4 import BeautifulSoup
from pydub import AudioSegment

import warnings
warnings.filterwarnings("ignore")

from config import *


headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'}

def get_soup(url):
    try:
        res_req = requests.get(url, headers=headers, cookies={'beget': 'begetok'}, verify=False) 
    except requests.exceptions.Timeout as t:
        print(t)
        print('Repeat request')
        res_req = requests.get(url, headers=headers, cookies={'beget': 'begetok'}, verify=False, timeout=15)
    html_text = res_req.content
    soup = BeautifulSoup(html_text, 'lxml')
    return soup


def mkdir(path_dir):
    '''
    Create directory
    Args:
        path_dir - path of directory to create
    '''
    if not os.path.exists(path_dir):
        os.mkdir(path_dir)
        print(path_dir, 'was created')
    else:
        print(path_dir, 'already exist')
        
def text_tofile(data_dir, i, text):
    file_name = create_filename(i)
    if file_name is None:
        print('Error with creating file')
        return
    
    with open(data_dir + file_name +'.txt', 'w') as f:
        f.write(text)
    
    return file_name

def create_filename(k):
    '''
    Create txt file name
    Args:
        k - counter
    '''
    numb_name = str(k)
    if len(numb_name)>5:
        return None
    while len(numb_name)<5:
        numb_name = '0%s' %numb_name
    return '%s' %(numb_name)



def time2msec(hmsms):
    '''
    Get time of subtitles in milliseconds
    Args:
        h:m:s,ms - time in hours, minutes, seconds, milliseconds
    '''
    hms, ms = hmsms.split(',')
    ms = int(ms)
    h, m, s = list(map(int, hms.split(':')))
    msec = ((h * 60 + m) * 60 + s) * 1000 + ms
    return msec


def crop_audio(id_video, step=10):
    '''
    Args:
        step - in minutes
    '''
    
    out_video_dir = crop_data_dir + id_video + '/'
    mkdir(out_video_dir)

    audio_file = '%s.mp4' %id_video

    #Get audio from mp4 file 
    sound = AudioSegment.from_file(source_dir + audio_file, 'mp4')

    len_sound = len(sound) / 60000 #minutes
    start_crop = 0
    end_crop = step

    while len_sound > 0:
        out_file = create_filename(end_crop)

        start_msec = start_crop * 60000
        end_msec = end_crop * 60000
        sound[start_msec:end_msec].export('%s_%s.wav' %(out_video_dir + id_video, out_file), format="wav")

        len_sound -= step
        start_crop = end_crop
        end_crop += step