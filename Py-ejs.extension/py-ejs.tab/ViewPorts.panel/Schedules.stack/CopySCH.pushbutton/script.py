"""
Copy schedule grid and columns titles

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

Schedule support added by @ejs-ejs
github.com/ejs-ejs | @ejs-ejs
0.1.0
TESTED REVIT API: 2022

0.2.0
2022 @2022-07-11
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
from schedule_wrapper import ScheduleSheetWrapper


if __name__ == '__main__':
    
    app = _HostApplication()
    logger = script.get_logger()
    
    if app.is_newer_than(2021, True):
      tempfile = script.get_document_data_file(42, 'dat')
      logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))
      script.clipboard_copy('Revit >=2021. Using document\'s data file {}'.format(tempfile))
    else:
      tempfile = os.path.join(gettempdir(), 'ScheduleDefinitions')
      logger.info('Revit <2021. Using temporary file')
    

    
    selection = rpw.ui.Selection()
    
    if len(selection) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'Select a single Schedule.')
            exit(0);
    #UI.TaskDialog.Show('py-ejs', 'Selected object is {}'.format(selection[0].unwrap()))
    if type(selection[0].unwrap()) in [DB.ScheduleSheetInstance]:
        el = selection[0].unwrap()
        
        #UI.TaskDialog.Show('pyRevitPlus', 'Schedules not implemented yet')
        #exit(1);
        shd = ScheduleSheetWrapper(el)
        origin = shd.placement
        
        
        
        
        msg = 'Saved schedule format to {}'.format(tempfile)
        
        #pt = Point(origin.X, origin.Y, origin.Z)
        if app.is_newer_than(2021, True):
          
          definitions = shd.definition
          msg =''
          
          shd_def = dict()
          shd_def['sGT'] = definitions.ShowGrandTotal
          shd_def['sGTC'] = definitions.ShowGrandTotalCount
          shd_def['sGTT'] = definitions.ShowGrandTotalTitle
          shd_def['GTT'] = definitions.GrandTotalTitle
            
          script.store_data('ScheduleDefinitions', shd_def)
          msg = msg + 'Saved schedule definition to {}\n'.format(tempfile)
          
          stor_data = dict()
          
          for idx in range(shd.definition.GetFieldCount()):
        #    
            field = shd.definition.GetField(idx)
        #    print("\nparsing field #{}".format(idx))
        #    
        #    Name = field.GetName()
        #    Heading = field.ColumnHeading
        #    Align = field.HorizontalAlignment
        #    width = field.GridColumnWidth
        #    hidden = field.IsHidden
        #    FO = field.GetFormatOptions()
        #    if not(FO.UseDefault):
        #      Accuracy = FO.Accuracy
        #      symTypeId = FO.GetSymbolTypeId()
        #      sym = symTypeId.TypeId
        #      usePlus = FO.UsePlusPrefix
            
        #   # flds{idx} = inst
        #    print("Field: {}, hidden?: {} , heading: '{}', Align: {}, width: {}\' ({} mm), format: {} \n".format(Name, hidden,  Heading, Align, width, width*12*25.4, 'default'))
        #    
        #    if not(FO.UseDefault):
        #      print("\t accuracy: {}, symbol: '{}', '+' prefix?: {} \n".format(Accuracy, sym, usePlus))
           
           # print("\nparsing field #{} of {}".format(idx, shd.definition.GetFieldCount()-1))
            tmp = revit.serialize(field)
            stor_data[idx] = tmp
           # print(stor_data)
           
           #stor_data = revit.serialize(definitions)
          #print(stor_data)
          script.store_data('ScheduleColumnDefinitions', stor_data)
          msg = msg +'Saved schedule grid and columns to {}'.format(tempfile)
           
        else:
          with open(tempfile, 'wb') as fp:
              pickle.dump(pt, fp)
          
        UI.TaskDialog.Show('py-ejs', msg)
        #print(msg)
    else:
        UI.TaskDialog.Show('py-ejs', 'This is not a schedule on a sheet')

  #__window__.Close()
