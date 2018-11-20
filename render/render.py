#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2011 Rene Dohmen <acidjunk@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# This script will produce a set of scales based on one predefined scale in all keys
import os

SIZES = [60, 80, 100, 120, 140, 160, 180, 200, 220]

TEMPLATE = """\\version "2.19.82"

\paper {{
    indent=0\mm
    line-width=200\mm
    oddFooterMarkup=##f
    oddHeaderMarkup=##f
    bookTitleMarkup = ##f
    scoreTitleMarkup = ##f
}}

\layout {{
    \override Staff.TimeSignature #'stencil = ##f
}}

<<

\\transpose c {transpose} {{
    \chords {{
        {chords}
    }}
}}

\\transpose c {transpose} {{
    {{
        {notes}
    }}
}}
>>
"""


class Render:
    def __init__(self, renderPath, name="riff"):
        self.renderPath = renderPath
        self.name = name
        self.sizes = SIZES
        self.settings = []
        self.notes = ""  # lilypond notation of notes
        self.chords = ""  # lilypond notation of chords
        self.riffs = []  # list of riffs for the riff renderer
        self.transposes = []  # list of notes and transpose messages for the riff renderer

        self.currentKey = 'c'  # init it to C
        # render to all keys by default
        self.rootKeys = ['c', 'cis', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'aes', 'a', 'ais', 'bes', 'b']

        self.cleff = "treble"

        self.lilypond = "/usr/local/bin/lilypond"
        self.octaves = {"-1": ",", "0": None, "1": "'", "2": "''"}

    def set_rootKeys(self, rootKeys):
        # allow to set new rootkey
        self.rootkey = []  # init empty again to allow looped access
        self.rootKeys = rootKeys

    def set_cleff(self, cleff):
        self.cleff = cleff

    def addNotes(self, notes):
        self.notes = notes

    def addChords(self, chords):
        self.chords = chords
    
    def addRiff(self, riff):
        # calls to addRiff should be prefixed by calls to doTranspose
        self.riffs.append(riff)

    def doTranspose(self, key):
        self.currentKey = key

    def render(self):
        # create folders when needed
        for size in self.sizes:
            if not os.path.exists("%s/%s" % (self.renderPath, size)):
                print("Creating folder: %s/%s" % (self.renderPath, size))
                os.makedirs("%s/%s" % (self.renderPath, size))
        if not os.path.exists("%s/svg" % self.renderPath):
            print("Creating folder: svg")
            os.makedirs("%s/svg" % self.renderPath)

        for file_postfix, octave in self.octaves.items():
            file_name = "%s/%s" % (self.renderPath, self.name)
            if octave:
                file_name = "%s_%s" % (file_name, file_postfix)
                output_file_name = "%s_%s" % (self.name, file_postfix)
            else:
                file_name = "%s" % file_name
                output_file_name = self.name

            tranpose = "%s%s" % (self.currentKey, octave if octave else "")
            lilypond_string = TEMPLATE.format(transpose=tranpose, notes=self.notes, chords=self.chords)
            print("%s.ly" % file_name)
            fHandle = open("%s.ly" % file_name, 'w')
            fHandle.write(lilypond_string)
            fHandle.close()
            for size in self.sizes:
                # #PNG
                cmd = "%s -s -dbackend=eps -dresolution=%s --png -o %s/%s/%s %s.ly" % (self.lilypond, size,
                                                                                       self.renderPath, size,
                                                                                       output_file_name, file_name)
                os.system(cmd)
                #SVG
                cmd = "%s -s -dbackend=svg -dcrop -o %s/svg/%s %s.ly" % (self.lilypond, self.renderPath, output_file_name,
                                                                         file_name)
                os.system(cmd)
                # mv cropped file over paper sized file:
                os.system('mv %s/svg/%s.cropped.svg %s/svg/%s.svg' % (self.renderPath, output_file_name,
                                                                      self.renderPath, output_file_name))
        return True
