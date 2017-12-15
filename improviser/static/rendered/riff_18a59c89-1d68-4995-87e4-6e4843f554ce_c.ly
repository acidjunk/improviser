\transpose c c {
{
\version "2.12.3"
\clef treble
\time 4/4
\override Staff.TimeSignature #'stencil = ##f
r4 es''16 d''8 c''16 c''8 bes'8 r4 bes'8 r16 bes'16 r4 r8 c''16 r16 r4 
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