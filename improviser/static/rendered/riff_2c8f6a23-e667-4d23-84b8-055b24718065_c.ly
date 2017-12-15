\transpose c c {
{
\version "2.12.3"
\clef treble
\time 4/4
\override Staff.TimeSignature #'stencil = ##f
c' d' ees' f' g' a' bes' c'' c'' d'' ees'' f'' g'' a'' bes'' c''' 
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