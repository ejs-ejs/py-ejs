"""
Restore Levels

Restore the view dependant properties of the saved levels
Only single segment (i.e. non-split) levles are supported yet
Levle leaders are added as needed, but there is no API to restore them

Only saved levels will be restored. If there are preselected levels, 
  only they will be restored.
Handy to fine-tune separate parts of the drawing


TESTED REVIT API: 2020

@ejs-ejs
This script is part of PyRevitPlus: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

def restore_levels_post2021():
  import os
  import pickle
  from tempfile import gettempdir
  from collections import namedtuple
  
  from pprint import pprint

  import rpw
  from rpw import doc, uidoc, DB, UI
  
  app = _HostApplication()
  logger = script.get_logger()

  tempfile = script.get_document_data_file(42, 'dat')
  logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))

  cView = doc.ActiveView
  Levels = rpw.ui.Selection()


  logger.info('[py-ejs]: Support for \'{}\' view type is experimental!'.format(cView.ViewType))

  if len(Levels) < 1:
    Levels = rpw.db.Collector(view=cView, of_class='Level').get_elements(wrapped=False)
  
  LevelLines = script.load_data('LevelLines', this_project=True)
#pprint(LevelLines)
    
  n=0

  for cLevel in Levels:
    #axis = cLevel.unwrap()
    if not(isinstance(cLevel, DB.Level)):
      cLevel = cLevel.unwrap()
            
    if isinstance(cLevel, DB.Level):
      # UI.TaskDialog.Show('pyRevitPlus', 'Level element \'{}\''.format(cLevel.Name))
      
      #pprint(cLevel.Name)
      
      if cLevel.Name in LevelLines:
      
        #pprint(cLevel.Name)
        
        #UI.TaskDialog.Show('pyRevitPlus', 'Found saved level element \'{}\''.format(cLevel.Name))
        curves=cLevel.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
        if len(curves) <> 1:
          UI.TaskDialog.Show('pyRevitPlus', 'The level line is defined by {} curves, unable to proceed'.format(len(curves)))
        else:
          cCurve = curves[0]
          cGridData = LevelLines[cLevel.Name]
          
          #pprint(cGridData)
              
          tmp = cCurve.GetEndPoint(0)
              
          if abs(cView.ViewDirection.X) > abs(cView.ViewDirection.Y):
            pt0 = DB.XYZ(tmp.X, cGridData.start.y, tmp.Z)
          else:
            pt0 = DB.XYZ(cGridData.start.x, tmp.Y, tmp.Z)
                
          tmp = cCurve.GetEndPoint(1)
              
          if abs(cView.ViewDirection.X) > abs(cView.ViewDirection.Y):
            pt1 = DB.XYZ(tmp.X, cGridData.end.y, tmp.Z)
          else:
            pt1 = DB.XYZ(cGridData.end.x, tmp.Y, tmp.Z)
                        
          #pprint(pt0)
          #pprint(pt1)
          
          if DB.XYZ.DistanceTo(pt0, pt1) > 0.1:
            gridline = DB.Line.CreateBound(pt0, pt1)
            #  UI.TaskDialog.Show('pyRevitPlus','Restoring endpoints of the level \'{}\''.format(cLevel.Name))
            #pprint(gridline)
            #pprint(cGridData.__dict__)
            
            if cLevel.IsCurveValidInView(DB.DatumExtentType.ViewSpecific, cView, gridline):
              with rpw.db.Transaction('Restoring view-dependant endpoints of the level \'{}\''.format(cLevel.Name)):
                cLevel.SetCurveInView(DB.DatumExtentType.ViewSpecific, cView, gridline)

              #UI.TaskDialog.Show('pyRevitPlus','Restoring level \'{}\' placement'.format(cLevel.Name))

              with rpw.db.Transaction('Restoring view-dependant placement of the level \'{}\''.format(cLevel.Name)):
                if cGridData.starts_with_bubble and cGridData.start_bubble_visible:
                  cLevel.ShowBubbleInView(DB.DatumEnds.End0, cView)
              #    if 'Leader0Anchor' in cGridData:
              #      if not cLevel.GetLeader(DB.DatumEnds.End0, cView):
              #        cLeader = cLevel.AddLeader(DB.DatumEnds.End0, cView)
                      #        cLeader = cLevel.GetLeader(DB.DatumEnds.End0, cView)
                      #        cLeader.Anchor = DB.XYZ(cGridData['Leader0Anchor'].X, cGridData['Leader0Anchor'].Y, cGridData['Leader0Anchor'].Z)
                      #        cLeader.Elbow = DB.XYZ(cGridData['Leader0Elbow'].X, cGridData['Leader0Elbow'].Y, cGridData['Leader0Elbow'].Z)
                      #        cLeader.End = DB.XYZ(cGridData['Leader0End'].X, cGridData['Leader0End'].Y, cGridData['Leader0End'].Z)
                else:
                  cLevel.HideBubbleInView(DB.DatumEnds.End0, cView)
                  
                if cGridData.ends_with_bubble and cGridData.end_bubble_visible:
                  cLevel.ShowBubbleInView(DB.DatumEnds.End1, cView)
                  #  if 'Leader1Anchor' in cGridData:
                  #    if not cLevel.GetLeader(DB.DatumEnds.End1, cView):
                  #      cLeader = cLevel.AddLeader(DB.DatumEnds.End1, cView)
                        #        cLeader = cLevel.GetLeader(DB.DatumEnds.End1, cView)
                        #        cLeader.Anchor = DB.XYZ(cGridData['Leader1Anchor'].X, cGridData['Leader1Anchor'].Y, cGridData['Leader1Anchor'].Z)
                        #        cLeader.Elbow = DB.XYZ(cGridData['Leader1Elbow'].X, cGridData['Leader1Elbow'].Y, cGridData['Leader1Elbow'].Z)
                        #        cLeader.End = DB.XYZ(cGridData['Leader1End'].X, cGridData['Leader1End'].Y, cGridData['Leader1End'].Z)
                                            
                else:
                  cLevel.HideBubbleInView(DB.DatumEnds.End1, cView)
                      
              n += 1
          else:
            UI.TaskDialog.Show('pyRevitPlus','Zero lenght segment for Level \'{}\'. \n Probably the level is saved in the perpendicular view. \nSkipping.'.format(cLevel.Name) )
  if n<>1:
    msg = 'Restored placement for {} levels'.format(n)
  else:
    msg = 'Restored placement of the level \'{}\''.format(cLevel.Name)
  return msg


def restore_levels_pre2021():
  import os
  import pickle
  from tempfile import gettempdir
  from collections import namedtuple

  import rpw
  from rpw import doc, uidoc, DB, UI

  Point = namedtuple('Point', ['X', 'Y','Z'])

  tempfile = os.path.join(gettempdir(), 'LevelPlacement')

  cView = doc.ActiveView
  Levels = rpw.ui.Selection()

  if not(cView.ViewType == DB.ViewType.Section or cView == DB.ViewType.Elevation):
    UI.TaskDialog.Show('pyRevitPlus', 'View type \'{}\' not supported'.format(cView.ViewType))
  else:
    experimental = True
    UI.TaskDialog.Show('pyRevitPlus', 'Support for \'{}\' view type is experimental!'.format(cView.ViewType))

    if len(Levels) < 1:
      Levels = rpw.db.Collector(view=cView, of_class='Level').get_elements(wrapped=False)
      
    try:
      with open(tempfile, 'rb') as fp:
        LevelLines = pickle.load(fp)
    except IOError:
      UI.TaskDialog.Show('pyRevitPlus', 'Could not find saved placementof the level.\nSave placement first.')

    n=0

    for cLevel in Levels:
      #axis = cLevel.unwrap()
      if not(isinstance(cLevel, DB.Level)):
        cLevel = cLevel.unwrap()
            
      if isinstance(cLevel, DB.Level):
        # UI.TaskDialog.Show('pyRevitPlus', 'Level element \'{}\''.format(cLevel.Name))
        if cLevel.Name in LevelLines:
          #UI.TaskDialog.Show('pyRevitPlus', 'Found saved level element \'{}\''.format(cLevel.Name))
          curves=cLevel.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
          if len(curves) <> 1:
            UI.TaskDialog.Show('pyRevitPlus', 'The level line is defind by {} curves, unable to proceed', len(curves))
          else:
            cCurve = curves[0]
            cGridData = LevelLines[cLevel.Name]
              
            tmp = cCurve.GetEndPoint(0)
              
            if abs(cView.ViewDirection.X) > abs(cView.ViewDirection.Y):
              pt0 = DB.XYZ(tmp.X, cGridData['Start'].Y, tmp.Z)
            else:
              pt0 = DB.XYZ(cGridData['Start'].X, tmp.Y, tmp.Z)
                
            tmp1 = cCurve.GetEndPoint(1)
              
            if abs(cView.ViewDirection.X) > abs(cView.ViewDirection.Y):
              pt1 = DB.XYZ(tmp.X, cGridData['End'].Y, tmp.Z)
            else:
              pt1 = DB.XYZ(cGridData['End'].X, tmp.Y, tmp.Z)
              #pt1 = DB.XYZ(cGridData['End'].X, cGridData['End'].Y, tmp1.Z)
                        
            if DB.XYZ.DistanceTo(pt0, pt1) > 0.1:
              gridline = DB.Line.CreateBound(pt0, pt1)
                
            #  UI.TaskDialog.Show('pyRevitPlus','Restoring endpoints of the level \'{}\''.format(cLevel.Name))
              
            if cLevel.IsCurveValidInView(DB.DatumExtentType.ViewSpecific, cView, gridline):
              with rpw.db.Transaction('Restoring view-dependant endpoints of the level \'{}\''.format(cLevel.Name)):
                cLevel.SetCurveInView(DB.DatumExtentType.ViewSpecific, cView, gridline)

              #UI.TaskDialog.Show('pyRevitPlus','Restoring level \'{}\' placement'.format(cLevel.Name))

              with rpw.db.Transaction('Restoring view-dependant placement of the level \'{}\''.format(cLevel.Name)):
                if cGridData['StartBubble'] and cGridData['StartBubbleVisible']:
                  cLevel.ShowBubbleInView(DB.DatumEnds.End0, cView)
                  if 'Leader0Anchor' in cGridData:
                    if not cLevel.GetLeader(DB.DatumEnds.End0, cView):
                      cLeader = cLevel.AddLeader(DB.DatumEnds.End0, cView)
                      #        cLeader = cLevel.GetLeader(DB.DatumEnds.End0, cView)
                      #        cLeader.Anchor = DB.XYZ(cGridData['Leader0Anchor'].X, cGridData['Leader0Anchor'].Y, cGridData['Leader0Anchor'].Z)
                      #        cLeader.Elbow = DB.XYZ(cGridData['Leader0Elbow'].X, cGridData['Leader0Elbow'].Y, cGridData['Leader0Elbow'].Z)
                      #        cLeader.End = DB.XYZ(cGridData['Leader0End'].X, cGridData['Leader0End'].Y, cGridData['Leader0End'].Z)
                else:
                  cLevel.HideBubbleInView(DB.DatumEnds.End0, cView)
                  
                if cGridData['EndBubble'] and cGridData['EndBubbleVisible']:
                  cLevel.ShowBubbleInView(DB.DatumEnds.End1, cView)
                  if 'Leader1Anchor' in cGridData:
                    if not cLevel.GetLeader(DB.DatumEnds.End1, cView):
                      cLeader = cLevel.AddLeader(DB.DatumEnds.End1, cView)
                      #        cLeader = cLevel.GetLeader(DB.DatumEnds.End1, cView)
                      #        cLeader.Anchor = DB.XYZ(cGridData['Leader1Anchor'].X, cGridData['Leader1Anchor'].Y, cGridData['Leader1Anchor'].Z)
                      #        cLeader.Elbow = DB.XYZ(cGridData['Leader1Elbow'].X, cGridData['Leader1Elbow'].Y, cGridData['Leader1Elbow'].Z)
                      #        cLeader.End = DB.XYZ(cGridData['Leader1End'].X, cGridData['Leader1End'].Y, cGridData['Leader1End'].Z)
                                            
                else:
                  cLevel.HideBubbleInView(DB.DatumEnds.End1, cView)
                      
              n += 1
            else:
              UI.TaskDialog.Show('pyRevitPlus','Zero lenght segment for Level \'{}\'. \n Probably the level is saved in the perpendicular view. \nSkipping.'.format(cLevel.Name) )
  if n<>1:
    msg = 'Restored placement for {} levels'.format(n)
  else:
    msg = 'Restored placement of the level \'{}\''.format(cLevel.Name)
  return msg
  
  
if __name__ == '__main__':
  import rpw
  from rpw import doc, uidoc, DB, UI
  from pyrevit import script, revit, DB, _HostApplication

  app = _HostApplication()
  logger = script.get_logger()
  cView = doc.ActiveView
  
  if cView.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation]:
    if app.is_newer_than(2021, True):
      msg = restore_levels_post2021()
    else:
      msg = restore_levels_pre2021()
  
    logger.debug('[py-ejs]: {}'.format(msg))
    UI.TaskDialog.Show('py-ejs', msg)
    
  else:
    UI.TaskDialog.Show('py-ejs', 'View type \'{}\' not supported'.format(cView.ViewType))
  
  
