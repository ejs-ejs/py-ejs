"""
CopyPasteViewportPlacemenet
Copy placement of selected viewport or schedule

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
Viewport information is stored in the model's data files in API >=2021

"""

import os
import pickle
from tempfile import gettempdir
from collections import namedtuple

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
      script.clipboard_copy('Revit >=2021. Using document\'s data file {}'.format(tempfile))
    else:
      tempfile = os.path.join(gettempdir(), 'ViewPlacement')
      logger.info('Revit <2021. Using temporary file')
    

    
    selection = rpw.ui.Selection()
    
    if len(selection) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'Select a single Viewport or Schedule. No more, no less!')
            exit(0);
    #UI.TaskDialog.Show('py-ejs', 'Selected object is {}'.format(selection[0].unwrap()))
    if type(selection[0].unwrap()) in [DB.Viewport, DB.ScheduleSheetInstance]:
        el = selection[0].unwrap()
        if isinstance(el, DB.Viewport):
            vp = ViewPortWrapper(el)
            origin = vp.project_origin_in_sheetspace
            msg = 'Saved viewport placement to {}'.format(tempfile)
        else:
            #UI.TaskDialog.Show('pyRevitPlus', 'Schedules not implemented yet')
            #exit(1);
            shd = ScheduleSheetWrapper(el)
            origin = shd.placement
            msg = 'Saved schedule placement to {}'.format(tempfile)
        
        pt = Point(origin.X, origin.Y, origin.Z)
        if app.is_newer_than(2021, True):
          pt = DB.XYZ(origin.X, origin.Y, origin.Z)
          stor_pt = revit.serialize(pt)
          script.store_data('ViewPlacement', stor_pt)
        else:
          with open(tempfile, 'wb') as fp:
              pickle.dump(pt, fp)
          UI.TaskDialog.Show('py-ejs', msg)
    else:
        UI.TaskDialog.Show('py-ejs', 'Not a viewport or schedule selected')

  #__window__.Close()
