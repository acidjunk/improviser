\header {

  title = "Chord Test"

}

 sl = {

  \override NoteHead #'style = #'slash

  \override Stem #'transparent = ##t

}

nsl = {

  \revert NoteHead #'style

  \revert Stem #'transparent

}




\mel = {
d'8 f' a' c'' g' b' d'' f'' \bar "|" c''8 e'' g'' b'' b''2
}

chordline = \chordmode { s1 * 4
a1:m7 a1:m7 a1:m7 a1:m7
s1 * 4}


\score {

<<
\new ChordNames \chordline
\relative {

\clef treble

\time 4/4

\key a \minor

{\mel}}
}

