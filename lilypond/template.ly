\transpose c c {
    {
        \version "2.19.82"
        \clef treble
        \time 4/4
        \override Staff.TimeSignature #'stencil = ##f
        d'8 f' a' c'' g' b' d'' f'' \bar "|" c''8 e'' g'' b'' b''2
    }
}
\paper{
    indent=0\mm
    line-width=200\mm
    oddFooterMarkup=##f
    oddHeaderMarkup=##f
    bookTitleMarkup = ##f
    scoreTitleMarkup = ##f
}
