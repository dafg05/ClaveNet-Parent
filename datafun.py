import os
import sys
import shutil
from datetime import datetime

LEARNING_DIR = "learning"
MIDI_UTILS_DIR = "midiUtils"
HVO_PROCESSING_DIR = "hvo_processing"
RAW_DATA_DIR = "rawData"
TEST_DATA_DIR = "testData"
FULL_LEARNING_INPUT_DIR = LEARNING_DIR + "/processedData"
TEST_LEARNING_INPUT_DIR = LEARNING_DIR + "/testData"
PROCESSING_INPUT_DIR = HVO_PROCESSING_DIR + "/split"
MIDI_SPLIT_DIR = MIDI_UTILS_DIR + "/midi/split"
AUG_OUTPUT_DIR= MIDI_UTILS_DIR + "/midi/augOutput"
EXAMPLES_DIR = MIDI_UTILS_DIR + "/midi/examples"
PARTITION_DIR = HVO_PROCESSING_DIR + "/partitioned"
PROCESSING_OUTPUT_DIR = HVO_PROCESSING_DIR + "/processed"

sys.path.append(f"{sys.path[0]}/{MIDI_UTILS_DIR}")
sys.path.append(f"{sys.path[0]}/{HVO_PROCESSING_DIR}")

from hvo_processing import main as mp
from midiUtils import main as mu
from midiUtils import dataAug

def pipeline(isTest, aug=False):
    """
    Run data processing pipeline:
    1. Split midi files from midi utils module into two bar segments
    2. Move split files to processing module
    3. Process data (partition and serialize)
    4. Move processed data to learning module

    TODO: 
    - avoid augmenting swing files with non-swing files
    - figure out what to do with validation data
    - figure out what to do with inf in offsets
    - am i missing training data?
    - is random partitioning the way to go?
    """

    print("Running pipeline with test data" if isTest else "Running pipeline with full data")
    
    dataDir = TEST_DATA_DIR if isTest else RAW_DATA_DIR
    learning_input_dir = TEST_LEARNING_INPUT_DIR if isTest else FULL_LEARNING_INPUT_DIR

    if len(os.listdir(PROCESSING_INPUT_DIR)) > 0:
        raise Exception(f"Processing input directory {PROCESSING_INPUT_DIR} is not empty. Please clear it before moving.")
    if len(os.listdir(learning_input_dir)) > 0:
        # raise Exception(f"Learning input directory {learning_input_dir} is not empty. Please clear it before moving.")
        x = input(f"ATTENTION: Pipeline might overwrite the contents in {learning_input_dir}. Continue? Y/n:")
        if x != "Y":
            print("Aborting pipeline...")
            sys.exit(1)
        else:
            print("Continuing pipeline...")

    # split raw data into two bar segments
    mu.splitMidi(dataDir, MIDI_SPLIT_DIR)

    print("----------------------------------")
    print(f"Split midi, wrote to {MIDI_SPLIT_DIR}")
    print("----------------------------------")

    move_source_dir = MIDI_SPLIT_DIR
    if aug:
        move_source_dir = AUG_OUTPUT_DIR
        dataAugParams = {
            "datetime" : datetime.now().timestamp(),
            "seed" : 42,
            "preferredStyle" : "",
            "outOfStyleProb" : 0.3,
            "numTransformations" : 2,
            "numReplacements" : 2,
            "fixedPartsToReplace" : None,
            "numExamples" : len(os.listdir(EXAMPLES_DIR))
        }

        styleParams = {"preferredStyle": dataAugParams["preferredStyle"], "outOfStyleProb": dataAugParams["outOfStyleProb"]}
        # trasform whole data using data augmentation scheme, writing to data aug output dir
        dataAug.augmentationScheme(sourceDir=MIDI_SPLIT_DIR, outputDir=AUG_OUTPUT_DIR, examplesDir=EXAMPLES_DIR, styleParams=styleParams, numTranformations=dataAugParams["numTranformations"], numReplacements=dataAugParams["numReplacements"], fixedPartsToReplace=dataAugParams["fixedPartsToReplace"], seed=dataAugParams["seed"],debug=False)

        print("----------------------------------")
        print(f"Data augmentation with {dataAugParams['numTranformations']} transformations per file done.")
        print("----------------------------------")

    else:
        dataAugParams = None

    # move data to hvo_processing_input dir
    moveFiles(move_source_dir, PROCESSING_INPUT_DIR, ["mid"])

    # preprocess collection of data. 
    mp.process(PROCESSING_INPUT_DIR, PROCESSING_OUTPUT_DIR, PARTITION_DIR, augParams=dataAugParams, debug=isTest)

    # move data to learning input dir
    moveFiles(PROCESSING_OUTPUT_DIR, learning_input_dir, ["pkl", "txt"])

    print("----------------------------------")
    print("Pipelining done!")
    print("----------------------------------")

def clear():
    """
    Clear all data from temp folders
    """
    print("----------------------------------")
    print("Clearing data from learning, midi_utils, and processing modules")
    print("----------------------------------")

    exToRemove = ["mid"]

    clearFiles(MIDI_SPLIT_DIR, exToRemove, removeDirs=False)
    clearFiles(AUG_OUTPUT_DIR, exToRemove, removeDirs=False)
    clearFiles(PROCESSING_INPUT_DIR, exToRemove, removeDirs=True)
    clearFiles(PROCESSING_OUTPUT_DIR, ["txt", "pkl"], removeDirs=False)
    clearFiles(PARTITION_DIR, extensionsToRemove=[], removeDirs=True)

    print("----------------------------------")
    print("Clearing done!")
    print("----------------------------------")


def moveFiles(sourceDir: str, targetDir: str, extensions: list):
    # move data to hvo_processing_input dir
    filesMoved = 0
    for f in os.listdir(sourceDir):
        ex = f.split(".")[-1]
        if ex in extensions:
            shutil.copyfile(sourceDir + '/' + f, targetDir + '/' + f)
            filesMoved += 1
    print("----------------------------------")
    print(f"Moved {filesMoved} files from {sourceDir} to {targetDir}")
    print("----------------------------------")


def clearFiles(dir: str, extensionsToRemove: list, removeDirs: bool):
    filesDeleted = 0
    dirsDeleted = 0
    for f in os.listdir(dir):
        # remove dir only if specified
        if os.path.isdir(dir + '/' + f) and removeDirs:
            shutil.rmtree(dir + '/' + f)
            dirsDeleted += 1
        else:
            if extensionsToRemove:
                ex = f.split(".")[-1]
                if ex in extensionsToRemove:
                    os.remove(dir + '/' + f)
                    filesDeleted += 1
    print(f"removed {filesDeleted} files and {dirsDeleted} directories from {dir}")

def usageAndExit():
    print("Usage: python dataAug.py <command> [aug]")
    print("command: 'fullpipe' or 'testpipe' or 'clear'")
    print("aug: 'aug'")
    exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usageAndExit()
    isTest = False
    aug = False
    if sys.argv[1] == "fullpipe":
        isTest = False
    elif sys.argv[1] == "testpipe":
        isTest = True
    elif sys.argv[1] == "clear":
        clear()
        sys.exit(0)
    else:
        usageAndExit()
    if len(sys.argv) > 2:
        if sys.argv[2] == "aug":
            aug = True
        else:
            usageAndExit()
    pipeline(isTest, aug)