"""
Save Grids

Save the view dependant properties - 
endpoint locations, grid heads and leaders
of the selected building grids for re-use

Non-grid elements will be skipped with dialog,
 so it's advisable to apply filtering beforehead

TESTED REVIT API: 2020

@ejs-ejs
This script is part of py-ejs: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

0.2.0
2021.1 @2022-07-11
Viewport information is stored in the model's data files in API >=2021

"""

def save_grids_post2021():
  import os
  import pickle
  from tempfile import gettempdir
  from collections import namedtuple

  import rpw
  from rpw import doc, uidoc, DB, UI
  from pyrevit import script, revit, DB, _HostApplication

  from pyrevit.coreutils import logger

  from pprint import pprint

  app = _HostApplication()
  logger = script.get_logger()

  tempfile = script.get_document_data_file(42, 'dat')
  logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))
  #  script.clipboard_copy('Revit >=2021. Using document\'s data file {}'.format(tempfile))
  
  cView = doc.ActiveView

  if cView.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation]:
    logger.debug('[py-ejs]: Support for \'{}\' view type is experimental!'.format(cView))
    
  selection = rpw.ui.Selection()

  n=0
  GridLines = dict()

  for cGrid in selection:
    el = cGrid.unwrap()
    if isinstance(el, DB.Grid):
      curves=el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
      if len(curves) <> 1:
        msg = 'The grid line is defined by {} curves, unable to proceed'.format(len(curves))
      else:
        #pprint(el)
        stor_pt = revit.serialize(el)
        GridLines[el.Name] = stor_pt
        n += 1
    
    if isinstance(el, DB.MultiSegmentGrid):
      logger.info('[py-ejs]: Skipping yet unsupported Multi-Segment grid \'{}\''.format(el.Name))
    else: 
      logger.info('[py-ejs]: Skipping non- grid element \'{}\''.format(el.Name))
            
  if n<>1:
    msg = 'Saved {} grid placements to {}'.format(n,tempfile)
  else:
    msg = 'Saved gris \'{}\' placement to {}'.format(cGridLine['Name'],tempfile)
     
        
  if n>0:
    script.store_data('GridLines', GridLines)
  else:
    msg = 'Nothing to save'
    
  return msg



def save_grids_pre2021():
  import os
  import pickle
  from tempfile import gettempdir
  from collections import namedtuple

  import rpw
  from rpw import doc, uidoc, DB, UI
  from pyrevit import script, revit, DB, _HostApplication

  from pyrevit.coreutils import logger

  from pprint import pprint

  Point = namedtuple('Point', ['X', 'Y','Z'])

  Axis = namedtuple('Axis', ['Name', 'Start', 'End','StartBubble', 'EndBubble', 'StartBubbleVisible', 'EndBubbleVisible'])

  app = _HostApplication()
  logger = script.get_logger()
    
  tempfile = os.path.join(gettempdir(), 'GridPlacement')
  logger.info('Revit <2021. Using temporary file')
  
  #script.clipboard_copy('Revit >=2021. Using document\'s data file {}'.format(tempfile))

  cView = doc.ActiveView

  if cView.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation]:
    logger.debug('[py-ejs]: Support for \'{}\' view type is experimental!'.format(cView))
    
  selection = rpw.ui.Selection()

  n=0
  GridLines = dict()

  for cGrid in selection:
    el = cGrid.unwrap()
    if isinstance(el, DB.Grid):
      curves=el.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
      if len(curves) <> 1:
        msg = 'The grid line is defined by {} curves, unable to proceed'.format(len(curves))
      else:
        cGridLine = {'Name':'', 'Start': Point(0,0,0), 'End': Point(0,0,0), 'StartBubble': False, 'StartBubbleVisible': False, 'EndBubble': False, 'EndBubbleVisible': False}
        
        cCurve = curves[0]
                
        leader0 = el.GetLeader(DB.DatumEnds.End0, cView)
        leader1 = el.GetLeader(DB.DatumEnds.End1, cView)
                
        if leader0:
          tmp = leader0.Elbow
          cGridLine['Leader0Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader0.End
          cGridLine['Leader0End'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader0.Anchor
          cGridLine['Leader0Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
                
        if leader1:
          tmp = leader1.Elbow
          cGridLine['Leader1Elbow'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader1.End
          cGridLine['Leader1End'] = Point(tmp.X, tmp.Y,tmp.Z)
          tmp = leader1.Anchor
          cGridLine['Leader1Anchor'] = Point(tmp.X, tmp.Y,tmp.Z)
            
        cGridLine['Name'] = el.Name
            
        tmp = cCurve.GetEndPoint(0)
        cGridLine['Start'] = Point(tmp.X, tmp.Y,tmp.Z)
                  
        tmp = cCurve.GetEndPoint(1)
        cGridLine['End'] = Point(tmp.X, tmp.Y,tmp.Z)
                
        if el.HasBubbleInView(DB.DatumEnds.End0, cView):
          cGridLine['StartBubble']=True
        if el.HasBubbleInView(DB.DatumEnds.End1, cView):
          cGridLine['EndBubble']=True
        if el.IsBubbleVisibleInView(DB.DatumEnds.End0, cView):
          cGridLine['StartBubbleVisible']=True
        if el.IsBubbleVisibleInView(DB.DatumEnds.End1, cView):
          cGridLine['EndBubbleVisible']=True
        if isinstance(cCurve, DB.Arc):
          tmp = cCurve.Center
          cGridLine['Center'] = Point(tmp.X, tmp.Y,tmp.Z)
                
        #pprint(cGridLine)
        GridLines[cGridLine['Name']] = cGridLine
        n += 1
    
    if isinstance(el, DB.MultiSegmentGrid):
      logger.info('[py-ejs]: Skipping yet unsupported Multi-Segment grid \'{}\''.format(el.Name))
    else: 
      logger.info('[py-ejs]: Skipping non- grid element \'{}\''.format(el.Name))
            
  if n<>1:
    msg = 'Saved {} grid placements to {}'.format(n,tempfile)
  else:
    msg = 'Saved gris \'{}\' placement to {}'.format(cGridLine['Name'],tempfile)
          
  if n>0:
    with open(tempfile, 'wb') as fp:
      pickle.dump(GridLines, fp)
      # close(fp)  
  else:
    msg = 'Nothing to save'
    
    
if __name__ == '__main__':
  import rpw
  from rpw import doc, uidoc, DB, UI
  from pyrevit import script, revit, DB, _HostApplication

  app = _HostApplication()
  logger = script.get_logger()
  cView = doc.ActiveView
  
  if cView.ViewType  in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan, DB.ViewType.Detail, DB.ViewType.AreaPlan, DB.ViewType.Section, DB.ViewType.Elevation]:
    if app.is_newer_than(2021, True):
      msg = save_grids_post2021()
    else:
      msg = save_grids_pre2021()
  
    logger.debug('[py-ejs]: {}'.format(msg))
    UI.TaskDialog.Show('py-ejs', msg)
    
  else:
    UI.TaskDialog.Show('py-ejs', 'View type \'{}\' not supported'.format(cView.ViewType))
  
  
