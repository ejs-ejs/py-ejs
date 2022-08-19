"""
Align Tags / Spot Elevations vertically

Align tags and Spot Elevations vertically, according to the preselected tag.

TESTED REVIT API: 2020, 2021

2021.1 @2022-06-29
Room tags are in DB.Architecture.RoomTag in API 2021.1

@ejs-ejs
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import os

import pyrevit
from pyrevit import HOST_APP

#from pyrevit import revit, DB, forms, script

import rpw
#from rpw import doc, uidoc, DB, UI


app = pyrevit._HostApplication()

from tags_wrapper import *


cView = doc.ActiveView
Tags = rpw.ui.Selection()


         
if cView.ViewType in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan, DB.ViewType.Detail, DB.ViewType.AreaPlan, DB.ViewType.Section, DB.ViewType.Elevation]:
        
    if len(Tags) < 1:
        UI.TaskDialog.Show('pyRevitPlus', 'A tag must preselected')
    if len(Tags) > 1:
        UI.TaskDialog.Show('pyRevitPlus', 'Select a SINGLE tag')
    else:
        cTag = Tags[0]
        if cTag.unwrap().GetType() in [DB.IndependentTag, DB.SpotDimension, 
          DB.SpatialElementTag, DB.Architecture.RoomTag]:
            if cTag.unwrap().GetType()  in [DB.IndependentTag, DB.SpatialElementTag ]:
                cPos = cTag.TagHeadPosition
            else:
              #  UI.TaskDialog.Show('pyRevitPlus', 'version {}'.format(app.version))
                if app.is_newer_than(2021, True):
                    # UI.TaskDialog.Show('pyRevitPlus', 'app is newer than 2020')
                    cPos = cTag.Origin  # API 2021.1
                else:
                    # UI.TaskDialog.Show('pyRevitPlus', 'app ios older than 2021')
                    cPos = cTag.Location.Point

                  
                

            with forms.WarningBar(title='Pick tag One by One. ESCAPE to end.'):
                if cView.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation]:
                    tag_align_XY(app, cTag.Category, cTag)
                else:
                    tag_align_X(cTag.Category, cTag)
        else:
            UI.TaskDialog.Show('pyRevitPlus', 'Selection is \"{}\", not a Tag or Spot Elevation'.format(cTag.unwrap().Category))
else:
    UI.TaskDialog.Show('pyRevitPlus', 'View type \'{}\' is not supported.'.format(cView.ViewType))
        