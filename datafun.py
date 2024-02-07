import os
import pathlib

SOURCE_DIR = 'preprocessing/preprocessedDatasets'
DESTINATION_DIR = 'learning/preprocessedDatasets'

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

copy_preprocessed_datasets(SOURCE_DIR, DESTINATION_DIR)