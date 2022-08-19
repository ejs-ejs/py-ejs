"""
CopyPasteViewportPlacement
Paste the placement of on selected viewport

TESTED REVIT API: 2015 | 2016 | 2017

@gtalarico
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/gtalarico | @gtalarico

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

Schedule support added by @ejs-ejs
github.com/ejs-ejs | @ejs-ejs
0.1.0
TESTED REVIT API: 2020

0.2.0
2021.1 @2022-07-11
Viewport information is retrievedf rom the model's data files in API >=2021
"""

import os
import pickle
from tempfile import gettempdir

import rpw
from rpw import doc, uidoc, DB, UI
from pyrevit import script, revit, DB, _HostApplication
#import pyrevit

from pyrevit.coreutils import logger
#log(__file__)
from viewport_wrapper import Point, ViewPortWrapper, move_to_match_vp_placment
from schedule_wrapper import ScheduleSheetWrapper, move_to_match_placement



if __name__ == '__main__':

    app = _HostApplication()
    logger = script.get_logger()
    
    if app.is_newer_than(2021, True):
      tempfile = script.get_document_data_file(42, 'dat')
      logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))
    else:
      tempfile = os.path.join(gettempdir(), 'ViewPlacement')
      logger.info('Revit <2021. Using temporary file')

    selection = rpw.ui.Selection()

    if len(selection) <> 1:
      UI.TaskDialog.Show('pyRevitPlus', 'Select single Viewport or Schedule. No more, no less!')
            
    if type(selection[0].unwrap()) in [DB.Viewport, DB.ScheduleSheetInstance]:
        ent = selection[0].unwrap()
        try:
            if app.is_newer_than(2021, True):
              #pt = pyrevit.DB.XYZ(origin.X, origin.Y, origin.Z)
              stor_pt = script.load_data('ViewPlacement', this_project=True)
              pt = stor_pt.deserialize()
            else:
              with open(tempfile, 'rb') as fp:
                pt = pickle.load(fp)
        except IOError:
            UI.TaskDialog.Show('pyRevitPlus', 'Could not find saved viewport or schedule placement.\nCopy a Viewport or Schedule placement first.')
        else:
            saved_pt = DB.XYZ(pt.X, pt.Y, pt.Z)
        if isinstance(ent, DB.Viewport):
            move_to_match_vp_placment(ent, saved_pt)
        else:
            move_to_match_placement(ent, saved_pt)
    else:
        UI.TaskDialog.Show('pyRevitPlus', 'Not a viewport or schedule selected')

  #__window__.Close()

