import shutil
import traceback
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from utils import *

from learning.training import process, training

TRAINING_RUNS_DIR = Path('train_runs')
TRAINING_OUT = Path('train_out')
TRAINING_ERROR_LOGS = 'train_errors.log'
HYPERPARAMS_SETTING = 'solar-shadow'
LOG_WANDB = True
IS_SMOL = True

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

if __name__ == '__main__':
    preprocessed_datasets = get_preprocessed_datasets(Path('../preprocessed_datasets', '1711057004'))
    train_pipeline(preprocessed_datasets, TRAINING_RUNS_DIR)