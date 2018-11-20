\version "2.19.82"

\paper {
            indent=0\mm
            line-width=200\mm
            oddFooterMarkup=##f
            oddHeaderMarkup=##f
            bookTitleMarkup = ##f
            scoreTitleMarkup = ##f
}

\layout {
	\override Staff.TimeSignature #'stencil = ##f
}


<<

\transpose c e {
  \chords {
	c2 g:sus4 f e
  }
}

\transpose c e {

  {
	d'8 f' a' c'' g' b' d'' f'' \bar "|" c''8 e'' g'' b'' b''2
  }
}
>>