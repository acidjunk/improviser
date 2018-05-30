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

import os, sys


class Render:
    def __init__(self, renderPath, name="riff"):
        self.renderPath = renderPath
        self.name = name
        self.lilypondVersion = '\\version "2.12.3"\n'
        self.sizes = [("small", 72), ("medium", 150), ("large", 300)]
        self.settings = []
        self.notes = []
        self.riffs = []  # list of riffs for the riff renderer
        self.transposes = []  # list of notes and transpose messages for the riff renderer

        self.currentKey = 'c'  # init it to C
        self.settings.append("""\\time 4/4\n""")  # set a very high value so all the exercises fit into 1 bar
        # self.settings.append("""\\override Staff.BarLine #'stencil = ##f\n""")
        self.settings.append("""\\override Staff.TimeSignature #'stencil = ##f\n""")
        self.rootKeys = ['c', 'cis', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'g', 'gis', 'aes', 'a', 'ais', 'bes',
                         'b']  # render to all keys by default
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
        #calculate filename
        if sys.platform=="win32": fileName=("%s\\%s" % (self.renderPath, self.name))
        else: fileName=("%s/%s" % (self.renderPath, self.name))
        print(fileName)
        fHandle=open("%s.ly" % fileName, 'w')

        fHandle.write("\\transpose c %s {\n" % self.currentKey)
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
            #render it in a couple of different dpi's and folders
            #self.sizes = [("small",72),("medium",150),("large",300)]
            cmd="%s -dbackend=eps -dresolution=%s --png -o %s/%s/%s %s.ly" % (self.lilypond, size[1], self.renderPath, size[0], self.name, fileName)
            print(cmd)
            os.system(cmd)
        return True
 
    
    def render_riff(self):
        #This renders a riff, it gets the key and major/minor from the caller
        #
        #calculate filename
        if sys.platform=="win32": fileName=("%s\\riff_%s_%s" % (self.renderPath, self.currentKey, self.name))
        else: fileName=("%s/riff_%s_%s" % (self.renderPath, self.currentKey, self.name))

        fHandle = open("%s.ly" % fileName, 'wb')

        # Will be set from the caller
        #fHandle.write("\\transpose c %s {\n" % self.currentKey) 
        fHandle.write("{\n")
        fHandle.write(self.lilypondVersion)
        fHandle.write("\\clef %s\n" % self.cleff)
        fHandle.write("\\key c \\major\n") 
        #for setting in self.settings:
        #    fHandle.write(setting)
        
        for riffTuple in self.riffs:
            notes = riffTuple[0]
            transpose = riffTuple[1].lower()
            chord = riffTuple[2]
            lyric = riffTuple[3]
            #handle the transpose:
            fHandle.write("\\transpose c %s {\n" % transpose)            
            #handle the notes
            for note in notes:
                print(note)
                fHandle.write(note + " ")
            fHandle.write("\n")
            fHandle.write("}\n") # end of transpose
            fHandle.write("\\addlyrics {\n%s\n}\n" % lyric)            

        fHandle.write("}\n")
        fHandle.write(self.paperFormat)

        fHandle.close()
        return "%s_%s" % (self.currentKey, self.name)    
