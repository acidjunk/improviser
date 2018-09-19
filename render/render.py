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


class Render:
    def __init__(self, renderPath, name="riff"):
        self.renderPath = renderPath
        self.name = name
        self.lilypondVersion = '\\version "2.12.3"\n'
        self.sizes = SIZES
        self.settings = []
        self.notes = []
        self.riffs = []  # list of riffs for the riff renderer
        self.transposes = []  # list of notes and transpose messages for the riff renderer

        self.currentKey = 'c'  # init it to C
        self.settings.append("""\\time 4/4\n""")  # set a very high value so all the exercises fit into 1 bar
        # self.settings.append("""\\override Staff.BarLine #'stencil = ##f\n""")
        self.settings.append("""\\override Staff.TimeSignature #'stencil = ##f\n""")
        # render to all keys by default
        self.rootKeys = ['c', 'cis', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'aes', 'a', 'ais', 'bes', 'b']
        self.paperFormat = """\paper{
            indent=0\mm
            line-width=120\mm
            oddFooterMarkup=##f
            oddHeaderMarkup=##f
            bookTitleMarkup = ##f
            scoreTitleMarkup = ##f
        }"""
        self.cleff = "treble"

        self.lilypond = "lilypond"
        self.octaves = {"-1": ",", "0": None, "1": "'", "2": "''"}

    def set_rootKeys(self, rootKeys):
        # allow to set new rootkey
        self.rootkey = []  # init empty again to allow looped access
        self.rootKeys = rootKeys

    def set_cleff(self, cleff):
        self.cleff = cleff

    def addNotes(self, notes):
        self.notes = []  # init empty again to allow looped access
        self.notes = notes

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

        for file_postfix, octave in self.octaves.items():
            file_name = "%s/%s" % (self.renderPath, self.name)
            if octave:
                file_name = "%s_%s" % (file_name, file_postfix)
                output_file_name = "%s_%s" % (self.name, file_postfix)
            else:
                file_name = "%s" % file_name
                output_file_name = self.name

            print("%s.ly" % file_name)
            fHandle = open("%s.ly" % file_name, 'w')

            fHandle.write("\\transpose c %s%s {\n" % (self.currentKey, octave if octave else ""))
            fHandle.write("{\n")
            fHandle.write(self.lilypondVersion)
            fHandle.write("\\clef %s\n" % self.cleff)
            #fHandle.write("\\key c \\major\n")
            for setting in self.settings:
                fHandle.write(setting)
            for note in self.notes:
                fHandle.write(note + " ")
            fHandle.write("\n")
            fHandle.write("}\n")
            fHandle.write("}\n")
            fHandle.write(self.paperFormat)

            fHandle.close()
            for size in self.sizes:
                cmd="%s -dbackend=eps -dresolution=%s --png -o %s/%s/%s %s.ly" % (self.lilypond, size,
                                                                                  self.renderPath, size,
                                                                                  output_file_name, file_name)
                print(cmd)
                os.system(cmd)
        return True
