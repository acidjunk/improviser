\transpose c c {
{
\version "2.12.3"
\clef treble
\time 4/4
\override Staff.TimeSignature #'stencil = ##f
d''8 c''16 g'8 e' d''. c''16 g'4.. 
}
}
\paper{
            indent=0\mm
            line-width=120\mm
            oddFooterMarkup=##f
            oddHeaderMarkup=##f
            bookTitleMarkup = ##f
            scoreTitleMarkup = ##f
        }