"""
Save Levels

Save the view dependant properties - 
endpoint locations, level heads and leaders
of the selected building levels for re-use

Non-level elements will be skipped with dialog,
 so it's advisable to apply filtering beforehead

TESTED REVIT API: 2020

@ejs-ejs
This script is part of py-ejs: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

def save_levels_pre2021():
  import os
  import pickle
  from tempfile import gettempdir
  from collections import namedtuple
  
  from pprint import pprint

  import rpw
  from rpw import doc, uidoc, DB, UI
  from pyrevit import script, revit, DB, _HostApplication

  app = _HostApplication()
  logger = script.get_logger()

  Point = namedtuple('Point', ['X', 'Y','Z'])

  Axis = namedtuple('Axis', ['Name', 'Start', 'End','StartBubble', 'EndBubble', 'StartBubbleVisible', 'EndBubbleVisible'])

  tempfile = os.path.join(gettempdir(), 'LevelPlacement')
  logger.info('Revit <2021. Using temporary file')

  cView = doc.ActiveView

  logger.info('[py-ejs]: Support for \'{}\' view type is experimental!'.format(cView.ViewType))
        
  selection = rpw.ui.Selection()


  n=0
  LevelLines = dict()

  for cLevel in selection:
    el = cLevel.unwrap()
  
    if isinstance(el, DB.Level):
      curves=el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
        
      if len(curves) <> 1:
        msg = 'The level line is defined by {} curves, unable to proceed'.format(len(curves))
      else:
        cLevelLine = {'Name':'', 'Start': Point(0,0,0), 'End': Point(0,0,0), 'StartBubble': False, 'StartBubbleVisible': False, 'EndBubble': False, 'EndBubbleVisible': False}
        
        cCurve = curves[0]

        leader0 = el.GetLeader(DB.DatumEnds.End0, cView)
        if leader0:
          tmp = leader0.Elbow
          cLevelLine['Leader0Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader0.End
          cLevelLine['Leader0End'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader0.Anchor
          cLevelLine['Leader0Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
                
            
        leader1 = el.GetLeader(DB.DatumEnds.End1, cView)
        if leader1:
          tmp = leader1.Elbow
          cLevelLine['Leader1Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader1.End
          cLevelLine['Leader1End'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader1.Anchor
          cLevelLine['Leader1Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
        
        cLevelLine['Name'] = el.Name
        
        tmp = cCurve.GetEndPoint(0)
        cLevelLine['Start'] = Point(tmp.X, tmp.Y,tmp.Z)
        tmp = cCurve.GetEndPoint(1)
        cLevelLine['End'] = Point(tmp.X, tmp.Y,tmp.Z)
        if el.HasBubbleInView(DB.DatumEnds.End0, cView):
          cLevelLine['StartBubble']=True
        if el.HasBubbleInView(DB.DatumEnds.End1, cView):
          cLevelLine['EndBubble']=True
        if el.IsBubbleVisibleInView(DB.DatumEnds.End0, cView):
           cLevelLine['StartBubbleVisible']=True
        if el.IsBubbleVisibleInView(DB.DatumEnds.End1, cView):
          cLevelLine['EndBubbleVisible']=True
            
        LevelLines[cLevelLine['Name']] = cLevelLine
        n += 1
    else: 
      logger.info('[py-ejs]: Skipping non- level element \'{}\''.format(el.Name))
        
        
  if n<>1:
    msg = 'Saved {} level placements to {}'.format(n,tempfile)
  else:
    msg = 'Saved level \'{}\' placement to {}'.format(cLevelLine['Name'],tempfile)
 
  if n>0:
    with open(tempfile, 'wb') as fp:
      pickle.dump(LevelLines, fp)
      # close(fp)
  else:
    msg = 'Nothing to save'
  return msg
      
def save_levels_post2021():
  import os
  import pickle
  from tempfile import gettempdir
  from collections import namedtuple
  
  from pprint import pprint

  import rpw
  from rpw import doc, uidoc, DB, UI
  from pyrevit import script, revit, DB, _HostApplication

  app = _HostApplication()
  logger = script.get_logger()
  cView = doc.ActiveView

  tempfile = script.get_document_data_file(42, 'dat')
  logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))

  logger.info('[py-ejs]: Support for \'{}\' view type is experimental!'.format(cView.ViewType))
        
  selection = rpw.ui.Selection()

  n=0
  LevelLines = dict()

  for cLevel in selection:
    el = cLevel.unwrap()
  
    if isinstance(el, DB.Level):
      curves=el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
        
      if len(curves) <> 1:
        UI.TaskDialog.Show('py-ejs', 'The level line is defined by {} curves, unable to proceed', len(curves))
        logger.debug('[py-ejs]: The level line is defined by {} curves, unable to proceed', len(curves))
      else:
        #UI.TaskDialog.Show('py-ejs', 'Data dump: {}'.format(GridLines))
        #pprint(el)
        stor_pt = revit.serialize(el)
        LevelLines[el.Name] = stor_pt
        n += 1
        
    else: 
      #UI.TaskDialog.Show('py-ejs', 'Skipping non- level element \'{}\''.format(el.Name))
      logger.info('[py-ejs]: Skipping non- level element \'{}\''.format(el.Name))
        
        
  if n<>1:
    msg = 'Saved {} level placements to {}'.format(n,tempfile)
  else:
    msg = 'Saved level \'{}\' placement to {}'.format(el.Name,tempfile)
 
  if n>0:
    script.store_data('LevelLines', LevelLines)
  else:
    msg = 'Nothing to save'
      
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
      msg = save_levels_post2021()
    else:
      msg = save_levels_pre2021()
  
    logger.debug('[py-ejs]: {}'.format(msg))
    UI.TaskDialog.Show('py-ejs', msg)
  else:
    UI.TaskDialog.Show('py-ejs', 'View type \'{}\' not supported'.format(cView.ViewType))
  
    

    
