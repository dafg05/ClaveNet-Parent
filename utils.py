from pathlib import Path
import os
import shutil

PREPROCESSED_KEYWORD = 'PreProcessed'

def get_preprocessed_datasets(preprocess_run_dir):
    return [Path(preprocess_run_dir, pre_dir) for pre_dir in os.listdir(preprocess_run_dir) if is_preprocessed_dataset_dir(pre_dir)]

def is_preprocessed_dataset_dir(dir: str):
    keyword = dir.split('_')[0]
    return keyword == PREPROCESSED_KEYWORD

def clear_dir(dir):
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)