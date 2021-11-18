# Speaker text identification

The goal is to collect text data that celebrity said.

##Data structure
/Data/twitter contains text files with phrases
/Data/youtube contains:
                      /source with audio and subtitles in txt, mp4, wav files downloaded from Youtube;
                              name of each file is id Youtube video
                      /crop with audio chunks in video folders
                      /rttm with diarization results for chunks
                      /dialogues with conversations; 
                                 in each video folders:
                                                    speaker_labels.json: {'speaker_name': 'speaker_label'}
                                                    dialog_labels.txt: 'speaker_label' 'text_file_name'
                                                    txt folder with text files of conversation
                                                    

##Tutorials
General pipeline with all steps: https://github.com/katianosikova/speaker-text-identification/blob/main/Pipeline.ipynb
