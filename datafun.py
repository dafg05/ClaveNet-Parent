import os
import sys
import shutil

LEARNING_DIR = "learning"
MIDI_UTILS_DIR = "midiUtils"
PROCESSING_DIR = "processing"
RAW_DATA_DIR = "rawData"
TEST_DATA_DIR = "testData"
FULL_LEARNING_INPUT_DIR = LEARNING_DIR + "/processedData"
TEST_LEARNING_INPUT_DIR = LEARNING_DIR + "/testData"
PROCESSING_INPUT_DIR = PROCESSING_DIR + "/split"
MIDI_UTILS_OUTPUT_DIR = MIDI_UTILS_DIR + "/midi/split"
PARTITION_DIR = PROCESSING_DIR + "/partitioned"
PROCESSING_OUTPUT_DIR = PROCESSING_DIR + "/processed"

sys.path.append(f"{sys.path[0]}/{MIDI_UTILS_DIR}")
sys.path.append(f"{sys.path[0]}/{PROCESSING_DIR}")

from processing import main as mp
from midiUtils import main as mu

def pipeline(isTest):
    """
    Run data processing pipeline:
    1. Split midi files from midi utils module into two bar segments
    2. Move split files to processing module
    3. Process data (partition and serialize)
    4. Move processed data to learning module
    """

    print("Running pipeline with test data" if isTest else "Running pipeline with full data")
    
    dataDir = TEST_DATA_DIR if isTest else RAW_DATA_DIR
    learning_input_dir = TEST_LEARNING_INPUT_DIR if isTest else FULL_LEARNING_INPUT_DIR

    # split raw data into two bar segments
    mu.splitMidi(dataDir, MIDI_UTILS_OUTPUT_DIR)

    # move split data to preprocess dir
    if len(os.listdir(PROCESSING_INPUT_DIR)) > 0:
        raise Exception(f"Processing input directory {PROCESSING_INPUT_DIR} is not empty. Please clear it before moving.")
    filesMoved = 0
    for f in os.listdir(MIDI_UTILS_OUTPUT_DIR):
        if f.endswith(".mid"):
            shutil.copyfile(MIDI_UTILS_OUTPUT_DIR + '/' + f, PROCESSING_INPUT_DIR + '/' + f)
            filesMoved += 1

    print("----------------------------------")
    print(f"Moved {filesMoved} files from {MIDI_UTILS_OUTPUT_DIR} to {PROCESSING_INPUT_DIR}")
    print("----------------------------------")

    # preprocess collection of data. 
    mp.process(PROCESSING_INPUT_DIR, PROCESSING_OUTPUT_DIR, PARTITION_DIR) 
    if len(os.listdir(learning_input_dir)) > 0:
        raise Exception(f"Learning input directory {learning_input_dir} is not empty. Please clear it before moving.")
    filesMoved = 0

    # move processed data to learning dir
    for f in os.listdir(PROCESSING_OUTPUT_DIR):
        if f.endswith(".pkl"):
            shutil.copyfile(PROCESSING_OUTPUT_DIR + '/' + f, learning_input_dir + '/' + f)
            filesMoved += 1

    print("----------------------------------")
    print(f"Moved {filesMoved} files from {PROCESSING_OUTPUT_DIR} to {learning_input_dir}")
    print("----------------------------------")

    print("----------------------------------")
    print("Pipelining done!")
    print("----------------------------------")

def clear():
    """
    Clear all data from midi_utils, and processing modules
    """
    print("----------------------------------")
    print("Clearing data from learning, midi_utils, and processing modules")
    print("----------------------------------")

    # clear midi_utils module output
    filesDeleted = 0
    for f in os.listdir(MIDI_UTILS_OUTPUT_DIR):
        os.remove(MIDI_UTILS_OUTPUT_DIR + '/' + f)
        filesDeleted += 1
    print(f"removed {filesDeleted} files from {MIDI_UTILS_OUTPUT_DIR}")

    # clear processing module input
    filesDeleted = 0
    dirsDeleted = 0
    for f in os.listdir(PROCESSING_INPUT_DIR):
        if os.path.isdir(PROCESSING_INPUT_DIR + '/' + f):
            shutil.rmtree(PROCESSING_INPUT_DIR + '/' + f)
            dirsDeleted += 1
        else:
            os.remove(PROCESSING_INPUT_DIR + '/' + f)
            filesDeleted += 1
    print(f"removed {filesDeleted} files and {dirsDeleted} directories from {PROCESSING_INPUT_DIR}")

    # clear processing module output
    filesDeleted = 0
    for f in os.listdir(PROCESSING_OUTPUT_DIR):
        os.remove(PROCESSING_OUTPUT_DIR + '/' + f)
        filesDeleted += 1
    print(f"removed {filesDeleted} files from {PROCESSING_OUTPUT_DIR}")

    # clear processing partitions
    dirsDeleted = 0
    for f in os.listdir(PARTITION_DIR):
        if os.path.isdir(PARTITION_DIR + '/' + f):
            shutil.rmtree(PARTITION_DIR + '/' + f)
            dirsDeleted += 1
    print(f"removed {dirsDeleted} directories from {PARTITION_DIR}")

    print("----------------------------------")
    print("Clearing done!")
    print("----------------------------------")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please specify a command. Valid commands are 'fullpipe', 'testpipe' and 'clear'")
        exit(1)
    if sys.argv[1] == "fullpipe":
        pipeline(False)
    elif sys.argv[1] == "testpipe":
        pipeline(True)
    elif sys.argv[1] == "clear":
        clear()
    else:
        print(f"Unknown command {sys.argv[1]}")
        exit(1)