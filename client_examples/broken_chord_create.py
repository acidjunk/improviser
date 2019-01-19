# Generate broken chord for M7, m7 en Dominant 7 chords in such a way that you get riffs that start on each chord note to ensure maximum instrument efficency
from collections import deque

note_numbers = ["1", "3", "5", "7"]

template_notes = {
    'Minor 7:Cm7': ['c', 'ees', 'g', 'bes'],
    'Major 7:Cmaj7': ['c', 'e', 'g', 'b'],
    'Dominant 7:C7': ['c', 'e', 'g', 'bes'],
}

for description, notes in template_notes.items():
    for i, note in enumerate(notes):
        octave = ''
        # use each note as a starting point once
        riff = []
        title, chord = description.split(":")
        name = f"{title} chord broken up starting on {note_numbers[i]}"
        print(name)
        note_collection = deque(notes)
        note_collection.rotate(i)
        for note in note_collection:
            riff.append(f"{note}{octave} ")

        note_collection[0] = f"{note_collection[0]}'"
        note_collection.rotate(-1)

        for note in note_collection:
            riff.append(f"{note}{octave} ")

        note_collection[0] = f"{note_collection[0]}'"
        note_collection.rotate(-1)

        for note in note_collection:
            riff.append(f"{note}{octave} ")

        note_collection[0] = f"{note_collection[0]}'"
        note_collection.rotate(-1)

        for note in note_collection:
            riff.append(f"{note}{octave} ")

        print("".join(riff))
