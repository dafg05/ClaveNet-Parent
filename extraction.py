from pathlib import Path
import shutil

from midiUtils import tools
import mido

TOONTRACK_MIDI_PACK = Path('toontrack_pack')
TOONTRACK_MIDI_EXTRACTED_ALL_GENRES = Path('toontrack_extracted_all-genres')
TOONTRACK_MIDI_EXTRACTED_SELECTED_GENRES = Path('toontrack_extracted_selected-genres')
TRIMMED_TOON_TRACK_MIDI_ALL_GENRES = Path('toontrack_trimmed_all-genres')
TRIMMED_TOON_TRACK_MIDI_SELECTED_GENRES = Path('toontrack_trimmed_selected-genres')

GENRE_DICT = {
    1: 'NO-GENRE',
    2: 'SALSA',
    3: 'GUAGUANCO',
    4: 'SONGO',
    5: 'CABALLO',
    6: 'MERENGUE',
    7: 'CUBAN-MAMBO',
    8: 'MOZAMBIQUE',
    9: 'CHA-CHA-CHA',
    10: 'PLENA',
    20: 'TIMBA',
    30: 'BOMBA',
    40: 'CHARANGA',
    50: 'CUBAN-6#8',
    60: 'INTRO-PICKUPS'
}

SELECTED_GENRES = ['SALSA', 'GUAGUANCO', 'SONGO', 'MERENGUE', 'CUBAN-MAMBO', 'MOZAMBIQUE', 'CHA-CHA-CHA']


def get_dirs(path: Path):
    return [dir for dir in path.iterdir() if dir.is_dir()]


def get_genre(dir: Path):
    id = dir.name.split('@')[0][:2]
    return GENRE_DICT[int(id)]


def is_fill(sub_dir: Path):
    return 'FILL-IN' in sub_dir.name

def extract_midi_from_toontrack_midi_pack(midi_pack_dir: Path, out_dir: Path, all_genres=False):
    # Extract midi files from the toontrack midi pack directory structure.
    # Only extract midi files from the selected genres.
    # Additionally, skip the fill-in midi files.

    for dir in get_dirs(midi_pack_dir):
        genre = get_genre(dir)
        print(f"Processing dir {dir.name}. Genre: {genre}")
        if (not all_genres) and (genre not in SELECTED_GENRES):
            continue

        for sub_dir in get_dirs(dir):
            info = sub_dir.name.split('@')[-1]
            if is_fill(sub_dir):
                continue

            print(f"Processing sub_dir {sub_dir.name}. Info: {info}")

            copy_counter = 0
            for file in sub_dir.iterdir():
                if file.suffix == '.mid':
                    new_name = f"{genre}_{info}_{file.name}"
                    new_path = Path(out_dir, new_name)
                    shutil.copy(file, new_path) 

                    copy_counter += 1

    return len(list(out_dir.glob('*.mid')))

def trim_midi_files(midi_dir: Path, out_dir: Path, beats_per_bar: int=4):
    midi_paths = list(midi_dir.glob('*.mid'))

    midi_paths = midi_paths
    for midi_path in midi_paths:
        mido_file = mido.MidiFile(midi_path)

        # get old track
        track = mido_file.tracks[0]

        # extract first 2 bars
        first_trim = tools.trimMidiTrack(track, 0, 2, beats_per_bar, mido_file.ticks_per_beat)
        new_midi_file = mido.MidiFile(ticks_per_beat=mido_file.ticks_per_beat)
        new_midi_file.tracks.append(first_trim)
        new_midi_file.save(Path(out_dir, f"{midi_path.stem}_trim1.mid"))

        # extract second 2 bars
        second_trim = tools.trimMidiTrack(track, 2, 4, beats_per_bar, mido_file.ticks_per_beat)
        new_midi_file = mido.MidiFile(ticks_per_beat=mido_file.ticks_per_beat)
        new_midi_file.tracks.append(second_trim)
        new_midi_file.save(Path(out_dir, f"{midi_path.stem}_trim2.mid"))
    
    return len(list(out_dir.glob('*.mid')))

if __name__ == "__main__":
    # extracted = extract_midi_from_toontrack_midi_pack(TOONTRACK_MIDI_PACK, TOONTRACK_MIDI_EXTRACTED_SELECTED_GENRES, all_genres=False)
    # print(f"Extracted {extracted} midi files.")

    trimmed = trim_midi_files(TOONTRACK_MIDI_EXTRACTED_SELECTED_GENRES, TRIMMED_TOON_TRACK_MIDI_SELECTED_GENRES)
    print(f"Trimmed {trimmed} midi files.")