import os
import mido


def transpose_file(source_fn, dest_fn, semitones):
    dest_dir = os.path.dirname(dest_fn)
    os.makedirs(dest_dir, exist_ok=True)

    midi_file = mido.MidiFile(source_fn)
    for message in midi_file.tracks[0]:
        if message.type in ("note_on", "note_off"):
            message.note += semitones

    midi_file.save(dest_fn)


key_map = {
    "C": 0,
    "D": 2,
    "E": 4,
    "F": 5,
    "G": 7,
    "A": 9,
    "B": 11,
}

reverse_key_map = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B"
}


def string_key_to_offset(key: str):
    """args:
    key: str - C, D#, Eb, G# ...

    returns numerical key representation as an offset from "C" key
    """

    offset = 0

    if key.endswith("#"):
        offset += 1
    elif key.endswith("b"):
        offset -= 1

    offset += key_map[key[0]]
    return offset



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=str,
        required=True,
        help="Source directory with all the MIDI files to be transposed",
    )
    parser.add_argument(
        "--dest-dir",
        type=str,
        required=True,
        help="Destination directory for the transposed MIDI files.",
    )

    args = parser.parse_args()

    for fn in [os.path.join(args.source_dir, fn) for fn in next(os.walk(args.source_dir))[2]]:

        fn_parts = os.path.basename(fn).split("_")
        key = fn_parts[1]

        minor = False
        # Remove the possible 'minor' part after the key (Gm -> G)
        if key.endswith("m"):
            key = key[:-1]
            minor = True
        
        key_int = string_key_to_offset(key)

        for target_key in range(12):
            target_key_str = reverse_key_map[target_key] + ("m" if minor else "")
            target_fn = fn_parts[0] + "_" + target_key_str + "_".join(fn_parts[2:])
            transpose_semitones = target_key - key_int

            transpose_file(fn, os.path.join(args.dest_dir, reverse_key_map[target_key], target_fn), transpose_semitones)
