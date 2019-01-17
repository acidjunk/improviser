# Generate broken chord for M7, m7 en Dominant 7 chords in such a way that you get riffs that start on each chord note to ensure maximum instrument efficency


note_numbers = ["I", "III", "V", "VII"]

template_notes = {
    'Minor 7:Cm7': ['c', 'ees', 'g', 'bes'],
    'Major 7:Cmaj7': ['c', 'e', 'g', 'b'],
    'Dominant 7:C7': ['c', 'e', 'g', 'bes'],
}

for description,notes in template_notes.items():
    for i, note in enumerate(notes):
        title, chord = description.split(":")
        name = f"{title} chord broken up starting on {note_numbers[i]}"
        print(name)

