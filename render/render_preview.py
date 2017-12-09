# # -*- coding: utf-8 -*-
# # Copyright (c) 2011 R Dohmen www.formatics.nl
# #
# # The renderer will render all riffs that have the isRendered value 0
# # It will triggered by system cron or web2py cron.
# # You can also just run it from this folder from the cmd line it will process all needed files
#
# import os,sys,socket
#
# db_path = '../databases'
#
# hostname=socket.gethostname()
# if hostname=="fountain.braintrainerplus.com":
#     sys.path.append('/webdir/www.riffcreator.com')
#     sys.path.append('/webdir/www.riffcreator.com/applications/improviser/models')
# else:
#     sys.path.append('/home/acidjunk/GIT/formatics.improviser')
#     sys.path.append('/home/acidjunk/GIT/formatics.improviser/applications/improviser/models')
#
# from gluon.dal import DAL, Field
# db = DAL('sqlite://storage.sqlite', folder=db_path, auto_import=True)
#
#
# from gluon.storage import Storage
# settings = Storage()
# settings.rootKeys=['c', 'cis', 'des', 'd', 'dis', 'ees', 'e', 'f', 'fis', 'ges', 'g', 'gis', 'aes', 'a', 'ais', 'bes', 'b']
# settings.cleanLilypondFiles=True # clean lilypond files after rendering?
#
#
# rows=db(db.riff.isRendered==0).select()
# if not rows:
#     print "No rendering needed."
#     sys.exit()
#
# from render import *
# keys=settings.rootKeys
# myRenderer=Render()
#
# for row in rows: #render all needed records
#     db.riff[row.id]=dict(isRendered=1)# set render state to busy
#     db.commit()
#     for key in keys:
#         myRenderer.name="riff_%s_%s" % (row.id, key)
#         notes=row.lilypond.split(" ")
#         myRenderer.addNotes(notes)
#         myRenderer.set_cleff(row.clef)
#         myRenderer.doTranspose(key)
#         if not myRenderer.render():
#             print "Error: couldn't render row.id: %s" % row.id
#     db.riff[row.id]=dict(isRendered=2)# set render state to ready
#     db.commit()
#
# if settings.cleanLilypondFiles:
#     print "Cleaning the lilypond garbage from render folder..."
#     print "You can disable it for debug purposes."
#     print "Look in the settings file for: settings.cleanLilypondFiles"
#     print os.getcwd()
#     print os.system("sh clean.sh")
#
#
