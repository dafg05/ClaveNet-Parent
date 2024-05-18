from pathlib import Path
import random
import pandas as pd
import pickle

from learning.evaluation import analysis, evaluation, evalDatasets

from grooveEvaluator import plotting

EVAL_RUNS_DIR = Path('newest_eval_runs')
MODELS_DIR = Path('newest_models')
EVALUATION_SET_PATH = Path('AfroCuban_Validation_PreProcessed_On_03_04_2024_at_21_31_hrs')
REPORT_PATH = Path('wandb_training_runs_report.csv')
OUT_DIR = Path('newest_analysis_out')
N = 23

COMPLETE_ANALYSIS_DATA = OUT_DIR / 'complete_analysis'
REDUCED_ANALYSIS_DATA = OUT_DIR / 'reduced_analysis'

PICKLED_RESULTS = 'results.pkl'
TABLE_RESULTS = 'results.csv'
SAMPLES_LIST = 'samples_list.txt'
AUDIO_EVAL_SAMPLES = 'audio_eval'

def analysis_on_all_evals():
    eval_paths = []
    for run_dir in EVAL_RUNS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        for eval_path in run_dir.iterdir():
            if not eval_path.is_dir():
                continue
            eval_paths.append(eval_path)


    complete_data = analysis.analysis(eval_paths, REPORT_PATH)
    complete_analysis_df = pd.DataFrame(complete_data)

    reduced_data = analysis.analysis(eval_paths, REPORT_PATH, reduced_features=True)
    reduced_analysis_df = pd.DataFrame(reduced_data)

    return complete_analysis_df, reduced_analysis_df


def collect_analysis_data(analysis_df: pd.DataFrame, out_dir: Path, evaluation_set_path: Path, num_audio_samples: int, features):
    # Select random audio samples for audio eval
    random.seed(42)

    full_valid_set = evalDatasets.ValidationHvoDataset(evaluation_set_path)
    indices = random.sample(list(range(len(full_valid_set))), num_audio_samples)
    indices.sort()
    subset = [full_valid_set[ix] for ix in indices]
    with open(out_dir / SAMPLES_LIST, 'w+') as samples_file:
        # write the master ids of the selected hvo_sequences to a file
        for ix, hvo_sequence in zip(indices, subset):
            samples_file.write(f"Ix: {ix}; Master Id: {hvo_sequence.master_id}\n")

    baseline_row = analysis_df[analysis_df["num_transformations"] == 0].iloc[0]
    baseline_eval_path = Path(baseline_row["eval_path"])
    baseline_pkl_path = baseline_eval_path / PICKLED_RESULTS

    # for every model present in the analysis, collect data on it.
    for _, row in analysis_df.iterrows():
        eval_path = Path(row["eval_path"])

        num_transformations = row["num_transformations"]
        num_replacements = row["num_replacements"]
        out_of_style_prob = row["out_of_style_prob"]

        model_start_time = row["model_name"].split("_")[-1]
        if num_transformations == 0:
            model_desc = "baseline"
        else:
            model_desc= f"t={num_transformations}_r={num_replacements}_o={out_of_style_prob}"

        results_dir = out_dir / f"{model_start_time}_{model_desc}"
        results_dir.mkdir(parents=True, exist_ok=True)

        # write a table with distance metrics info
        table_df = pd.read_csv(eval_path / TABLE_RESULTS, index_col='feature')
        table_df = table_df.loc[features]
        table_df.to_csv(results_dir / TABLE_RESULTS)

        # plot the distance metrics
        pkl_path = eval_path / PICKLED_RESULTS
        with open(pkl_path, 'rb') as pkl_file:
            results_dict = pickle.load(pkl_file)
            results_dict = {feat: results_dict[feat] for feat in features}

            # plot with respect to the baseline
            with open(baseline_pkl_path, 'rb') as baseline_pkl_file:
                baseline_results_dict = pickle.load(baseline_pkl_file)
                baseline_results_dict = {feat: baseline_results_dict[feat] for feat in features}

                comparison_figname = f"Comparison to Validation Set ({model_desc.replace('_', ', ')})"
                plotting.plot_multiple_distance_metrics(results_dict, baseline_results_dict, f"Model {model_start_time}", "Baseline",results_dir, figname=comparison_figname, non_negative_klds=True)

        # do audio eval
        model_path = MODELS_DIR / f'{row["model_name"]}.pth'
        audio_dir = results_dir / AUDIO_EVAL_SAMPLES
        audio_dir.mkdir(parents=True, exist_ok=True)
        evaluation.audioEval(audio_dir, model_path, full_valid_set, indices)

        
if __name__ == "__main__":
    complete_df, reduced_df = analysis_on_all_evals()
    complete_df.to_csv(OUT_DIR / "complete_analysis.csv")
    print(f"Complete analysis data written to csv file at {OUT_DIR / 'complete.csv'}")

    reduced_df.to_csv(OUT_DIR / "reduced_analysis.csv")
    print(f"Reduced analysis data written to csv file at {OUT_DIR / 'reduced.csv'}")

    collect_analysis_data(complete_df, COMPLETE_ANALYSIS_DATA, EVALUATION_SET_PATH, 10, analysis.EVAL_FEATURES)
    collect_analysis_data(reduced_df, REDUCED_ANALYSIS_DATA, EVALUATION_SET_PATH, 10, analysis.REDUCED_EVAL_FEATURES)
