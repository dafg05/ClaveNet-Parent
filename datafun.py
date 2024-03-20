import os
import pathlib
from tqdm import tqdm
from preprocessing import preprocessing as pre

SOURCE_DIR = 'preprocessing/preprocessedDatasets'
DESTINATION_DIR = 'learning/preprocessedDatasets'
PREPROCESSING_OUT_DIR = 'pre_out'

NUM_TRANSFORMATION_VALUES = [1, 2, 3]
NUM_REPLACEMENT_VALUES = [1, 2, 3, 4]
OUT_OF_STYLE_PROB_VALUES = [0.0, 0.25, 0.5, 0.75, 1.0]

TEST = True

def copy_preprocessed_datasets(source_dir, destination_dir):
    """
    Copy the preprocessed datasets from the source_dir to the destination_dir. Don't overwrite existing datasets in the destination dir.
    TODO: test me
    """
    source_dir = pathlib.Path(source_dir)
    destination_dir = pathlib.Path(destination_dir)
    for file in source_dir.iterdir():
        # note that the data sets are folders.
        if file.is_dir():
            if not (destination_dir / file.name).exists():
                print(f'Copying {file.name} to {destination_dir}...')
                os.system(f'cp -r {file} {destination_dir}')
            else:
                print(f'{file.name} already exists in the destination directory. Skipping...')

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

def batch_preprocess_datasets():
    # get data aug params combinations
    # for each combination, do a preprocessing run. copy the output to the cluster
    combinations = get_data_aug_params_combinations(NUM_TRANSFORMATION_VALUES, NUM_REPLACEMENT_VALUES, OUT_OF_STYLE_PROB_VALUES)

    if TEST:
        combinations = combinations[0:2]

    for data_aug_params in tqdm(combinations, desc="Batch preprocessing datasets"):
        print(f"Current param combination: {data_aug_params}")
        pre.preprocess(PREPROCESSING_OUT_DIR, data_aug_params)


if __name__ == "__main__":
    batch_preprocess_datasets()