import traceback
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from learning.evaluation import evaluation as eval

EVALUATION_RUNS_DIR = Path('eval_runs')
VALIDATION_DATASET = Path('AfroCuban_Validation_PreProcessed_On_03_04_2024_at_01_04_hrs')
EVALUATION_ERROR_LOGS = 'eval_errors.log'

def eval_pipeline(model_paths):
    # name each run with a timestamp
    time_str = str(int(datetime.now().timestamp()))
    run_dir = Path(EVALUATION_RUNS_DIR, time_str)
    Path.mkdir(run_dir, exist_ok=True)

    error_log_path = run_dir / EVALUATION_ERROR_LOGS
    with open(error_log_path, 'w') as f:
        f.write(f"Training error log for run {time_str} \n")

    error_count = 0
    for model_path in tqdm(model_paths, desc="Evaluation pipeline"):
        try:
            # evaluate the model
            evaluation_path = eval.evaluate(model_path, VALIDATION_DATASET, run_dir)
        except Exception as e:
            print("An error occured while evaluating the model.")
            with open(error_log_path, 'a') as f:
                f.write(f"Error evaluating model: {model_path}. Stack trace: {traceback.format_exc()} \n")
                error_count += 1


def get_model_paths(run_dir):
    return [model_path for model_path in run_dir.iterdir() if model_path.endswith('.pth')]
