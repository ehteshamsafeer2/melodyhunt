import os
import zipfile
from django.shortcuts import render
from django.http import HttpResponse
from .forms import SongUploadForm
from spleeter.separator import Separator

from django.http import HttpResponse
from django.shortcuts import render
import librosa
import librosa.display
from pydub import AudioSegment

def separate_instruments(request):
    print("Called")
    if request.method == 'POST':
        form = SongUploadForm(request.POST, request.FILES)
        print("checking form valid", form)
        if form.is_valid():
            print("form valid ... ")
            song = form.save()
            output_folder = os.path.join('media', 'output')
            os.makedirs(output_folder, exist_ok=True)

            # Process the song using Spleeter
            separator = Separator('spleeter:4stems')
            separator.separate_to_file(song.audio_file.path, output_folder)
            print(output_folder)

            file_list = os.listdir(output_folder)
            print(file_list )
            extract_segments(file_list)
            # Create a zip file containing the separated instrument tracks
            print("Zipping....")
            zip_file_path = os.path.join("media", "output", "melody.zip")
            with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for stem_name in os.listdir(output_folder):
                    stem_path = os.path.join(output_folder, stem_name)
                    if os.path.isdir(stem_path):
                        for root, _, files in os.walk(stem_path):
                            for file in files:
                                zipf.write(os.path.join(root, file), os.path.join(stem_name, file))

            # Provide the zip file as a download response
            with open(zip_file_path, 'rb') as zip_file:
                response = HttpResponse(zip_file.read())
                response['Content-Type'] = 'application/zip'
                response['Content-Disposition'] = f'attachment; filename="melody_generated.zip"'

            # Empty the output_folder
            path = output_folder
            for file_name in os.listdir(path):  
                print(file_name)
    # construct full file path
                file = path +'/'+ file_name
                os.remove(file)
            return response

    else:
        form = SongUploadForm() 
    return render(request, 'index.html', {'form': form})
 



def extract_segments(filepath):
    for dir in filepath:
        temp =  os.path.join('media', 'output')
        files = os.listdir(f'{temp}/{dir}')
        for i in files:
            if i != 'vocals.wav':
                music_file = os.path.join(temp,f'{dir}/{i}')
                audio = AudioSegment.from_file(music_file)
    
    # Calculate the total duration of the audio in milliseconds
                total_duration = len(audio)
    
    # Initialize variables for splitting
                start_time = 0
                end_time = 700
    
    # Create the output folder if it doesn't exist
                if not os.path.exists(f'{temp}/{dir}/{i}_'):
                    os.makedirs(f'{temp}/{dir}/{i}_')
    
                segment_number = 1
    
                while start_time < total_duration:
            # Ensure that the end time doesn't exceed the total duration
                    if end_time > total_duration:
                        end_time = total_duration
        
        # Extract the segment
                    segment = audio[start_time:end_time]
        
        # Define the output file name
                    output_file = os.path.join(f'{temp}/{dir}/{i}_', f'{i}_melody_{segment_number}.mp3')
        
        # Export the segment as an audio file
                    segment.export(output_file, format="mp3")
        
        # Update the start and end times for the next segment
                    start_time = end_time
                    end_time += 700
        
                    segment_number += 1