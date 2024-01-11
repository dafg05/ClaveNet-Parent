import numpy as np
import note_seq
import soundfile as sf
import sys
import os
import pypianoroll
import matplotlib

from PIL import Image
# from playsound import playsound

from note_seq import midi_io
from pretty_midi import PrettyMIDI

SF_PATH = "processing/hvo_sequence/soundfonts/Standard_Drum_Kit.sf2"
OUT_DIR = "out"
AUDIO_DIR = OUT_DIR + "/audio"
PLOTS_DIR = OUT_DIR + "/plots"
SR = 44100

def synthesize(midi_path, sr=SR):
    # ns = midi_io.midi_file_to_note_sequence(midi_path)
    # pm = note_seq.note_sequence_to_pretty_midi(ns)
    pm = PrettyMIDI(midi_path)
    audio = pm.fluidsynth(fs=sr, sf2_path=SF_PATH)
    return audio

def save_audio(audio, out_path, sr=SR):
    sf.write(out_path, audio, sr, 'PCM_24')

def visualize(midi_path):
    multitrack = pypianoroll.read(midi_path)
    # multitrack.plot()
    # print(multitrack)
    multitrack.plot().show()

def usageAndExit():
    print("Usage: python listening.py <listen or look> <midi_path>")
    sys.exit(1)

if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #     usageAndExit()
    
    # midi_path = sys.argv[2]
    # if not os.path.exists(midi_path):
    #     raise FileNotFoundError(f"Midi at {midi_path} does not exist.")
    
    # # get file name (without extension)
    # filename = midi_path.split("/")[-1]
    # filename = filename.split(".")[0]

    # if sys.argv[1] == "listen":
    #     # save audio to file
    #     # out_path = AUDIO_DIR + "/" + filename
    #     # save_audio(synthesize(midi_path=midi_path), midi_path)

    #     # # playback
    #     # playsound(out_path)
    #     print("not yet")
        
    # elif sys.argv[1] == "look":
    #     # save plot to file
    #     plotter = Plotter()
    #     out_path = PLOTS_DIR + "/" + filename + ".html"
    #     print(out_path)
    #     visualize(midi_path, out_path, plotter)

    #     # show image
    #     im = Image.open(out_path)
    #     im.show()

    # else:
    #     usageAndExit()

    visualize("test0.mid")

