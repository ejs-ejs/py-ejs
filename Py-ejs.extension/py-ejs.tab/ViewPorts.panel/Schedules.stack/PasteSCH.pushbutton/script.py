"""
Restore schedule column width and titles


--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

github.com/ejs-ejs | @ejs-ejs

TESTED REVIT API: 2022

0.1.0
2021.1 @2022-12-03
Schedule definition information is retrieved from the model's data files in API >=2021
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
from schedule_wrapper import ScheduleSheetWrapper



if __name__ == '__main__':

  app = _HostApplication()
  logger = script.get_logger()
    
  if app.is_newer_than(2021, True):
    tempfile = script.get_document_data_file(42, 'dat')
    logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))
  else:
    tempfile = os.path.join(gettempdir(), 'ScheduleColumnDefinitions')
    logger.info('Revit <2021. Using temporary file')

  selection = rpw.ui.Selection()

  if len(selection) <> 1:
    UI.TaskDialog.Show('pyRevitPlus', 'Select a Schedule')
            
  if type(selection[0].unwrap()) in [DB.ScheduleSheetInstance]:
    ent = selection[0].unwrap()
    try:
      if app.is_newer_than(2021, True):
        #pt = pyrevit.DB.XYZ(origin.X, origin.Y, origin.Z)
        shd_def = script.load_data('ScheduleDefinitions', this_project=True)
        definitions = script.load_data('ScheduleColumnDefinitions', this_project=True)
      else:
        with open(tempfile, 'rb') as fp:
          definitions = pickle.load(fp)
    except IOError:
      UI.TaskDialog.Show('Py-ejs', 'Could not find saved schedule definition.\nSave any first.')
      
######

  # 'ent' / 'shd' is the currently selected shedule,
  # 'definitions' are loaded schedule definitions
  
    shd = ScheduleSheetWrapper(ent)
  #  old_definitions = shd.definition
    
    #make a hash of name:index to speed thigs up
    saved_names = dict()
    for idx in range(len(definitions)):
      val = definitions[idx]
      saved_names[val.name] = idx
      
  #  print(definitions)
  #  print(saved_names)
  #  print(shd_def)
  
    displayGT = False
    if hasattr(shd_def,'sGT'):
      print("Show Gand Total: {}".format(shd_def['sGT']))
      displayGT = shd_def['sGT']
    if hasattr(shd_def,'sGTC'):
      print("Show Gand Total Count: {}".format(shd_def['sGTC']))
    if hasattr(shd_def,'sGTT'):
      print("Show Gand Total Title: {}".format(shd_def['sGTT']))
      if hasattr(shd_def,'GTT'):
        print("Show Gand Total Title: {} , '{}'".format(shd_def['sGTT'], shd_def['GTT']))
      
      
    if displayGT:
      with rpw.db.Transaction("Setting shedule parameters"):
        shd.definition.ShowGrandTotal = shd_def['sGT']
        shd.definition.ShowGrandTotalTitle = shd_def['sGTT']
        shd.definition.ShowGrandTotalCount = shd_def['sGTC']
        shd.definition.GrandTotalTitle = shd_def['GTT']
    else:
      with rpw.db.Transaction("Setting shedule parameters"):
        shd.definition.ShowGrandTotal = shd_def['sGT']
      #  shd.definition.GrandTotalTitle = shd_def['GTT']
    
      

    
    for idx in range(shd.definition.GetFieldCount()):
      
    #  print("\nparsing field #{} of {}".format(idx, shd.definition.GetFieldCount()-1))
      
      field = shd.definition.GetField(idx)
 #    print(field.names())
      
      # match field's name
      if field.GetName() in saved_names:
        column_definition = definitions[saved_names[field.GetName()]]
        #fo = field.GetFormatOptions()
        fo = DB.FormatOptions(DB.UnitTypeId.SquareMeters) # substitute for for FO_Units in the future perfect
        
        if hasattr(column_definition, 'FO'):
          if fo.UseDefault:
            print("Default units found. Will try to overwrite")
            #UI.TaskDialog.Show('Py-ejs', "The '{}' column currently uses project setting for the units.\nPlease untick it manually from 'Formatting->Field Format...'.\n    WE APOLOGIZE FOR \nI N C O N V E N I E N C E S".format(field.GetName()))

          #else:
          fo.UseDefault = False
          fo.RoundingMethod = DB.RoundingMethod.Nearest
          #  fo.SetUnitTypeId = DB.ForgeTypeId('autodesk.unit.symbol:mSup2-1.0.1')
          #fo_new.SetUnitTypeId = DB.UnitTypeId.SquareMeters # substitute for for FO_Units in the future perfect
          fo.Accuracy = column_definition.FO_Accuracy
          fo.UsePlusPrefix = column_definition.FO_usePlus
          fo.SetSymbolTypeId(DB.ForgeTypeId(column_definition.FO_sym))
        #  print("column alignment set to '{}'".format(column_definition.align))
          
        else:
          fo.UseDefault = True
        
        if fo.IsValidObject:
          with rpw.db.Transaction("Setting column '{}' parameters".format(field.GetName())):
            field.SetFormatOptions(fo)
            field.ColumnHeading = column_definition.heading
            field.SheetColumnWidth = column_definition.width
            field.IsHidden = column_definition.hidden
        
            if ('Center' == column_definition.align):
              field.HorizontalAlignment = DB.ScheduleHorizontalAlignment.Center
            if ('Left' == column_definition.align):
              field.HorizontalAlignment = DB.ScheduleHorizontalAlignment.Left
            if ('Right' == column_definition.align):
              field.HorizontalAlignment = DB.ScheduleHorizontalAlignment.Right
        else:
          print("something's wrong with the formatoptions")  
          
        
  
  #print("column hidden [{}] or unknown [{}]".format(field.IsHidden, field.GetName() in saved_names))
          
        
      
      
      
      
      
      #Name = field.GetName()
      #Heading = field.ColumnHeading
      #Align = field.HorizontalAlignment
      #width = field.SheetColumnWidth
      #hidden = field.IsHidden
      #FO = field.GetFormatOptions()
      #if not(FO.UseDefault):
      #  Accuracy = FO.Accuracy
      #  symTypeId = FO.GetSymbolTypeId()
      #  sym = symTypeId.TypeId
       # usePlus = FO.UsePlusPrefix
      
    #  print("Field: {}, hidden?: {} , heading: '{}', Align: {}, width: {}\' ({} mm)\n".format(field.GetName(), field.IsHidden, field.ColumnHeading, field.HorizontalAlignment, field.SheetColumnWidth, field.SheetColumnWidth*12*25.4))
      
      #if not( fo.UseDefault):
     #   print("\t accuracy: {}, symbol: '{}', '+' prefix?: {} \n".format(fo.Accuracy, column_definition.FO_sym, fo.UsePlusPrefix))
           
    
######      
  else:
    UI.TaskDialog.Show('Py-ejs', 'Not a viewport or schedule selected')

  #__window__.Close()



