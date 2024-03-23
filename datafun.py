import os
import shutil
import subprocess
import traceback
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from preprocessing import preprocessing as pre
from learning.training import process, training

DATA_TO_CLUSTER_SCRIPT = './dataToCluster.sh'
PREPROCESSING_RUNS_DIR = 'preprocessing_runs'
PREPROCESSING_OUT = 'pre_out'
TRAINING_ERROR_LOGS = 'preprocessing_errors.log'
PREPROCESSED_KEYWORD = 'PreProcessed'

TRAINING_RUNS_DIR = 'train_runs'
TRAINING_OUT = 'train_out'
TRAINING_ERROR_LOGS = 'train_errors.log'
HYPERPARAMS_SETTING = 'solar-shadow'
LOG_WANDB = True
IS_SMOL = True

NUM_TRANSFORMATION_VALUES = [1]
NUM_REPLACEMENT_VALUES = [1, 2, 4]
OUT_OF_STYLE_PROB_VALUES = [0.0, 0.5, 1.0]

TEST_TRANSFORMATION_VALUES = [1]
TEST_REPLACEMENT_VALUES = [1,2]
TEST_OUT_OF_STYLE_PROB_VALUES = [0.5]

def pre_processing_pipeline(test=True):
    # Preprocess dataset with different data augmentation parameters.
    # NOTE: Unfortunately, this pipeline can only be run on the local machine.

    # name each run with a timestamp
    time_str = str(int(datetime.now().timestamp()))
    run_path = Path(PREPROCESSING_RUNS_DIR, time_str)
    Path.mkdir(run_path, exist_ok=True)

    preprocess_out_dir = Path(run_path, PREPROCESSING_OUT)

    error_log_path = Path(run_path, TRAINING_ERROR_LOGS)
    with open(error_log_path, 'w') as f:
        f.write(f"Preprocessing error log for run {time_str} \n")

    if not test:
        combinations = get_data_aug_params_combinations(NUM_TRANSFORMATION_VALUES, NUM_REPLACEMENT_VALUES, OUT_OF_STYLE_PROB_VALUES)
    else:
        combinations = get_data_aug_params_combinations(TEST_TRANSFORMATION_VALUES, TEST_REPLACEMENT_VALUES, TEST_OUT_OF_STYLE_PROB_VALUES)

    error_count = 0
    for data_aug_params in tqdm(combinations, desc="Processing pipeline"):
        try:
            # preprocess the dataset
            pre.preprocess(preprocess_out_dir, data_aug_params)
            assert len(get_preprocessed_datasets(preprocess_out_dir)) == 1, "More than one preprocessed dataset found."
        
            # run dataToCluster.sh to copy the preprocessed dataset to hpc
            preprocessed_dataset = get_preprocessed_datasets(preprocess_out_dir)[0]
            result = subprocess.run([DATA_TO_CLUSTER_SCRIPT, preprocessed_dataset, time_str], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Error running dataToCluster.sh; error: {result.stderr}")

        except Exception as e:
            print("An error occured while preprocessing the dataset.")
            with open(error_log_path, 'a') as f:
                f.write(f"Error preprocessing with data aug params: {data_aug_params}. Stack trace: {e} \n")
                error_count += 1

        finally:
            # clear the preprocess_run_dir
            clear_dir(preprocess_out_dir)

    
    print(f"Preprocessed {len(combinations) - error_count} out of {len(combinations)} combinations. Errors written on {error_log_path}. Check cluster for processed datasets.")

def train_pipeline(preprocessed_datasets_paths, out_models_dir):
    # Process the preprocessed datasets on the cluster, and then train the models.

    # name each run with a timestamp
    time_str = str(int(datetime.now().timestamp()))
    run_path = Path(TRAINING_RUNS_DIR, time_str)
    Path.mkdir(run_path, exist_ok=True)

    error_log_path = Path(run_path, TRAINING_ERROR_LOGS)
    with open(error_log_path, 'w') as f:
        f.write(f"Training error log for run {time_str} \n")

    error_count = 0
    for ppd_path in tqdm(preprocessed_datasets_paths, desc="Training pipeline"):
        pd_path = None
        try:
            # process the preprocessed dataset
            pd_path = process.processing(ppd_path, TRAINING_RUNS_DIR)
            # train the model
            model_path = training.train(HYPERPARAMS_SETTING, pd_path, out_models_dir, LOG_WANDB, IS_SMOL)

        except Exception as e:
            print("An error occured while training the model.")
            with open(error_log_path, 'a') as f:
                f.write(f"Error training with preprocessed dataset: {ppd_path}. Stack trace: {traceback.format_exc()} \n")
                error_count += 1

        finally:
            # delete the processed dataset
            if pd_path is not None:
                shutil.rmtree(pd_path)
    

def evaluation_pipeline():
    pass

def get_data_aug_params_combinations(num_transformation_values, num_replacement_values, out_of_style_prob_values):
    combinations = []
    for t in num_transformation_values:
        for r in num_replacement_values:
            for o in out_of_style_prob_values:
                data_aug_params = {
                    "random_seed" : pre.RANDOM_SEED,
                    "seed_examples_sets" : pre.SEED_EXAMPLES_SETS,
                    "num_transformations" : t,
                    "num_replacements" : r,
                    "out_of_style_prob" : o
                }
                combinations.append(data_aug_params)
    return combinations

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

def get_preprocessed_datasets(preprocess_run_dir):
    return [Path(preprocess_run_dir, pre_dir) for pre_dir in os.listdir(preprocess_run_dir) if is_preprocessed_dataset_dir(pre_dir)]


if __name__ == "__main__":
    # Take in an argument to specify whether to run the preprocessing pipeline or the training pipeline.
    # If no argument is given, show usage and exit.
    import sys
    if len(sys.argv) != 2:
        print("Usage: python datafun.py <preprocess/train>")
        sys.exit(1)
    
    if sys.argv[1] == 'preprocess':
        pre_processing_pipeline()
    elif sys.argv[1] == 'train':
        preprocessed_datasets = get_preprocessed_datasets(Path('../preprocessed_datasets', '1711057004'))
        train_pipeline(preprocessed_datasets, TRAINING_RUNS_DIR)