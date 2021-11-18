from pyannote.database.util import load_rttm
import json

from utils import *
from config import *


class Dialog:
    def __init__(self, id_video, rttm_file_path, shift_mins):
        sub_file_name = source_dir + id_video + '.txt'        
        with open(sub_file_name, 'r') as f:
            self.subs = f.read()
        
        self.id_video = id_video        
        
        _, rttm_annot = load_rttm(rttm_file_path).popitem()
        self.rttm_json = rttm_annot.support(collar=1).for_json()
        
        rttm_labels = rttm_annot.labels()
        self.label_rttm_dict = dict(zip(rttm_labels, range(len(rttm_labels)))) 
        
        self.shift_mins = shift_mins
    
    def generate_rttm_timeline(self):
        if 'content' not in self.rttm_json:
            print('There are not content in RTTM')
            return

        shift = self.shift_mins * 60 #seconds

        content_rttm = self.rttm_json['content']
        for snippet in content_rttm:
            if ('segment' not in snippet) or ('label' not in snippet):
                print('Error with getting segment or label')
                break

            start_snippet = (snippet['segment']['start'] + shift) * 1000 
            end_snippet = (snippet['segment']['end'] + shift) * 1000
            label_snippet = self.label_rttm_dict[snippet['label']]
            yield {'start': int(start_snippet), 'end': int(end_snippet), 'label': label_snippet}
        
        
    def prepare_text(self, sub_text):
        #Remove all in [] and ()
        sub_text = re.sub(r'(\[[\w\s]+\])', '', sub_text)
        sub_text = re.sub(r'(\([\w\s]+\))', '', sub_text)

        #Prepare text
        sub_text = sub_text.lower()
        sub_text = re.sub(r'[^a-z^A-Z\s\d\.\?]', ' ', sub_text)
        sub_text = re.sub(r'(\w+)-\s(\w+)', r'\1 \2', sub_text)
        sub_text = sub_text.replace('--', '.')
        sub_text = sub_text.replace('\n', ' ')
        sub_text = ' '.join(sub_text.split())

        return sub_text

    def generate_sub_timeline(self):
        sub_list = self.subs.split('\n\n')

        shift = self.shift_mins * 60 * 1000 #mseconds

        for k, sub in enumerate(sub_list):
            num, sub_time, sub_text = sub.split('\n', maxsplit=2)
            start_time, end_time = sub_time.split(' --> ')
            start_sub = time2msec(start_time)
            end_sub = time2msec(end_time)
            if end_sub <= shift:
                continue
            sub_text = self.prepare_text(sub_text)
            if len(sub_text) == 0:
                continue
            yield {'start': start_sub, 'end': end_sub, 'text': sub_text}
            
            
    def label_dialog(self, label_dict):
        rttm_gen = self.generate_rttm_timeline()
        rttm = next(rttm_gen)

        sub_gen = self.generate_sub_timeline()
        sub = next(sub_gen)

        self.speaker_label_list = [rttm['label']]
        self.snippet_list = []
        snippet = sub['text']

        while True:
            try: 
                if abs(sub['end'] - rttm['end']) < 1000:    
                    self.snippet_list.append(snippet)

                    rttm = next(rttm_gen)
                    self.speaker_label_list.append(rttm['label'])

                    sub = next(sub_gen)
                    snippet = sub['text']

                else: 
                    if sub['end'] < rttm['end']:
                        sub = next(sub_gen)
                        snippet += ' ' + sub['text']
                    else:
                        rttm = next(rttm_gen)
                        
                        if rttm['start'] >= sub['end']:
                            self.snippet_list.append(snippet)
                            self.speaker_label_list.append(rttm['label'])

                            sub = next(sub_gen)
                            snippet = sub['text']

            except StopIteration as e:
                break

        if len(self.speaker_label_list) > len(self.snippet_list):
            self.snippet_list.append(snippet)

        return self.write(label_dict)


    def write(self, label_dict):
        i_sent = 0

        video_data_dir = '%s/' %(dialogues_dir + self.id_video)
        mkdir(video_data_dir)

        text_data_dir = video_data_dir + 'txt/'
        mkdir(text_data_dir)

        filename_list = []

        for i, snip in enumerate(self.snippet_list):
            sentence_list = [x.strip() for x in re.split('[\.\?\$]', snip) if len(x)>0]
            file_name = '%d_' %self.shift_mins + text_tofile(text_data_dir + '%d_' %self.shift_mins, i, '\n'.join(sentence_list))
            filename_list.append(file_name)
            i_sent += len(sentence_list)


        #Write labels for dialog
        filename_label_list = [' '.join(x) for x in list(zip(map(str, self.speaker_label_list), filename_list))]        
        dialog_labels = '\n'.join(filename_label_list) + '\n'
        with open(video_data_dir + 'dialog_labels.txt', 'a') as f:
            f.write(dialog_labels)

        #Write speaker labels
        with open(video_data_dir + 'speaker_labels.json', 'w') as f:
            json.dump(label_dict, f)

        return i_sent