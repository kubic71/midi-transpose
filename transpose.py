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


def batch_transpose(source_dir, dest_dir, pitch_offset):

    for fn in [os.path.join(source_dir, fn) for fn in next(os.walk(source_dir))[2]]:
        if not (fn.lower().endswith(".midi") or fn.lower().endswith(".mid")):
            print(f"skipping {fn}")
            continue

        print(f"Generating transpositions for {fn}")

        fn_parts = os.path.basename(fn).split("_")

        # normalize the style-part of the filename
        fn_parts[0] = fn_parts[0].lower().capitalize()

        key = fn_parts[1]

        minor = False
        # Remove the possible 'minor' part after the key (Gm -> G)
        if key.endswith("m"):
            key = key[:-1]
            minor = True
        
        key_int = string_key_to_offset(key)

        for target_offset in range(-6, 6):
            target_offset += pitch_offset
            target_scale = (key_int + target_offset) % 12
            target_key_str = reverse_key_map[target_scale] + ("m" if minor else "")


            target_fn = fn_parts[0] + "_" + target_key_str + "_" + "_".join(fn_parts[2:])
            target_dir = fn_parts[0] + "_" + target_key_str

            transpose_file(fn, os.path.join(dest_dir, target_dir, target_fn), target_offset)

    print("Done!")


if __name__ == "__main__":
    from tkinter import *
    from threading import *
    from tkinter import filedialog
    import functools

    window = Tk()
    window.title("Batch-transpose MIDI")
    # window.geometry('350x200')
    Label(window, text="Source directory").grid(row=0)
    Label(window, text="Destination directory").grid(row=1)
    Label(window, text="Pitch offset").grid(row=2)

    e1 = Entry(window)
    e2 = Entry(window)
    e3 = Entry(window)

    e1.grid(row=0, column=1)
    e2.grid(row=1, column=1)
    e3.grid(row=2, column=1)
    e3.insert(0, "0")

    def select_inp_dir():
        path = filedialog.askdirectory()
        e1.delete(0, END)
        e1.insert(0, path)

    def select_output_dir():
        path = filedialog.askdirectory()
        e2.delete(0, END)
        e2.insert(0, path)

    btn1 = Button(window, text="Select", command=select_inp_dir)
    btn2 = Button(window, text="Select", command=select_output_dir)
    btn1.grid(row=0, column=2)
    btn2.grid(row=1, column=2)

    def generate_after():
        sd = e1.get()
        dd = e2.get()
        ofs = int(e3.get())
        print("Source dir:", sd)
        print("Destination dir:", dd)
        print("Pitch offset:", ofs)

        # Call work function
        t1 = Thread(target=functools.partial(batch_transpose, source_dir=sd, dest_dir=dd, pitch_offset=ofs))
    
        t1.start()

        
    generate_btn = Button(window, text="Generate", command=generate_after)
    generate_btn.grid(row=3, column=0)

    window.mainloop()
