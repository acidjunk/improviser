\transpose c c {
{
\version "2.12.3"
\clef treble
\time 4/4
\override Staff.TimeSignature #'stencil = ##f
bes'8. bes'16 r4 bes'8. bes'16 r4 r8 bes'8 c''16 bes'8 es''16 r2 
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