"""
Restore Grids

Restore the view dependant properties of the saved grids
Only single segment (i.e. non-split) grids are supported yet
Grid leaders are added as needed, but there is no API to restore them

Only saved grids will be restored. If there are preselected grids, 
  only they will be restored.
Handy to fine-tune separate parts of the drawing



TESTED REVIT API: 2020

@ejs-ejs
This script is part of py-ejs: Extensions for PyRevit
github.com/ejs-ejs | @ejs-ejs

--------------------------------------------------------
RevitPythonWrapper: revitpythonwrapper.readthedocs.io
pyRevit: github.com/eirannejad/pyRevit

"""

import os
import pickle
from tempfile import gettempdir
from collections import namedtuple

import rpw
from rpw import doc, uidoc, DB, UI
from pyrevit import script, revit, DB, _HostApplication

from pprint import pprint

app = _HostApplication()
logger = script.get_logger()

Point = namedtuple('Point', ['X', 'Y','Z'])

if app.is_newer_than(2021, True):
  tempfile = script.get_document_data_file(42, 'dat')
  logger.info('Revit >=2021. Using document\'s data file {}'.format(tempfile))
else:
  tempfile = os.path.join(gettempdir(), 'GridPlacement')
  logger.info('Revit <2021. Using temporary file')

cView = doc.ActiveView
Axes = rpw.ui.Selection()


if cView.ViewType in [DB.ViewType.Section, DB.ViewType.Elevation]:
    experimental = True
    UI.TaskDialog.Show('py-ejs', 'Support for \'{}\' view type is experimental!'.format(cView.ViewType))
    

if cView.ViewType in [DB.ViewType.FloorPlan, DB.ViewType.CeilingPlan, DB.ViewType.Detail, DB.ViewType.AreaPlan, DB.ViewType.Section, DB.ViewType.Elevation]:
        
    if len(Axes) < 1:
            Axes = rpw.db.Collector(view=cView, of_class='Grid').get_elements(wrapped=False)
            inSelection = False
    else:
        inSelection = True

    if app.is_newer_than(2021, True):
      GridLines = script.load_data('GridLines', this_project=True)
      #pprint(GridLines)
      #pt = GridLines.deserialize()
    else:
      try:
        with open(tempfile, 'rb') as fp:
            GridLines = pickle.load(fp)
      except IOError:
        UI.TaskDialog.Show('py-ejs', 'Could not find saved placement of the grid.\nSave placement first.')

    n=0
    
    #UI.TaskDialog.Show('py-ejs', '{} grids to restore'.format(len(Axes)))

    for cAxis in Axes:
        if inSelection:
            cAxis = cAxis.unwrap()
        if isinstance(cAxis, DB.Grid):
            #UI.TaskDialog.Show('py-ejs', 'Grid element \'{}\''.format(cAxis.Name))

            if cAxis.Name in GridLines:
               # UI.TaskDialog.Show('py-ejs', 'Found saved grid element \'{}\''.format(cAxis.Name))
                curves=cAxis.GetCurvesInView(DB.DatumExtentType.ViewSpecific, cView)
                    
                cGridData = GridLines[cAxis.Name]
                #pprint(cGridData.__dict__)
                    
                if len(curves) <> 1:
                    UI.TaskDialog.Show('py-ejs', 'The grid line is defind by {} curves, unable to proceed', len(curves))
                else:
                    cCurve = curves[0]
                        

                    tmp = cCurve.GetEndPoint(0)
                    tmp1 = cCurve.GetEndPoint(1)
                        
                    if cView.ViewType in [DB.ViewType.Section,DB.ViewType.Elevation]:
                        #pt0 = DB.XYZ(tmp.X, tmp.Y, cGridData['Start'].Z)
                        #pt1 = DB.XYZ(tmp.X, tmp.Y, cGridData['End'].Z)
                      if app.is_newer_than(2021, True):
                        pt0 = DB.XYZ(cCurve.GetEndPoint(0).X, cCurve.GetEndPoint(0).Y, cGridData.start.z)
                      
                        pt1 = DB.XYZ(cCurve.GetEndPoint(0).X, cCurve.GetEndPoint(0).Y, cGridData.end.z)
                      else:
                        pt0 = DB.XYZ(cCurve.GetEndPoint(0).X, cCurve.GetEndPoint(0).Y, cGridData['Start'].Z)

                        pt1 = DB.XYZ(cCurve.GetEndPoint(0).X, cCurve.GetEndPoint(0).Y, cGridData['End'].Z)
                            
                    else:
                      #pt0 = DB.XYZ(cGridData['Start'].X, cGridData['Start'].Y, tmp.Z)
                      #pt1 = DB.XYZ(cGridData['End'].X, cGridData['End'].Y, tmp1.Z)
                      if app.is_newer_than(2021, True):
                       # pprint(cGridData.start.__dict__)
                        pt0 = DB.XYZ(cGridData.start.x, cGridData.start.y, cCurve.GetEndPoint(0).Z)

                        pt1 = DB.XYZ(cGridData.end.x, cGridData.end.y, cCurve.GetEndPoint(1).Z)
                      else:
                        pt0 = DB.XYZ(cGridData['Start'].X, cGridData['Start'].Y, cCurve.GetEndPoint(0).Z)
                        pt1 = DB.XYZ(cGridData['End'].X, cGridData['End'].Y, cCurve.GetEndPoint(1).Z)
                        
                    if isinstance(cCurve, DB.Arc):
                        #ptc = DB.XYZ(cGridData['Center'].X, cGridData['Center'].Y, tmp1.Z)
                        # take mid-point of the exixting curve as reference. Will cause trouble.
                        # should't, if the grid is not extremelly modified, eg, reversed
                        ptRef = cCurve.Evaluate(0.5, True) 
                        gridline = DB.Arc.Create(pt0, pt1, ptRef)
                    else:
                        gridline = DB.Line.CreateBound(pt0, pt1)

                  #  Restoring endpoints of the axis
                    if cAxis.IsCurveValidInView(DB.DatumExtentType.ViewSpecific, cView, gridline):
                        with rpw.db.Transaction('Restoring view-dependant endpoints if the grid \'{}\''.format(cAxis.Name)):
                            cAxis.SetCurveInView(DB.DatumExtentType.ViewSpecific, cView, gridline)

                    # Restoring axes

                    with rpw.db.Transaction('Restoring view-dependant placement of the grid \'{}\''.format(cAxis.Name)):
                      if app.is_newer_than(2021, True):
                        if cGridData.starts_with_bubble and cGridData.start_bubble_visible:
                          cAxis.ShowBubbleInView(DB.DatumEnds.End0, cView)
                        #  if 'Leader0Anchor' in cGridData:
                        #    if not cAxis.GetLeader(DB.DatumEnds.End0, cView):
                        #      cLeader = cAxis.AddLeader(DB.DatumEnds.End0, cView)
                        else:
                          cAxis.HideBubbleInView(DB.DatumEnds.End0, cView)
                        
                        if cGridData.ends_with_bubble and cGridData.end_bubble_visible:
                          cAxis.ShowBubbleInView(DB.DatumEnds.End1, cView)
                          #if 'Leader0Anchor' in cGridData:
                          #  if not cAxis.GetLeader(DB.DatumEnds.End1, cView):
                          #    cLeader = cAxis.AddLeader(DB.DatumEnds.End1, cView)
                        else:
                          cAxis.HideBubbleInView(DB.DatumEnds.End1, cView)
                        
                      else:
                        if cGridData['StartBubble'] and cGridData['StartBubbleVisible']:
                            cAxis.ShowBubbleInView(DB.DatumEnds.End0, cView)
                            if 'Leader0Anchor' in cGridData:
                                if not cAxis.GetLeader(DB.DatumEnds.End0, cView):
                                    cLeader = cAxis.AddLeader(DB.DatumEnds.End0, cView)
                            #        cLeader = cAxis.GetLeader(DB.DatumEnds.End0, cView)
                            #        cLeader.Anchor = DB.XYZ(cGridData['Leader0Anchor'].X, cGridData['Leader0Anchor'].Y, cGridData['Leader0Anchor'].Z)
                            #        cLeader.Elbow = DB.XYZ(cGridData['Leader0Elbow'].X, cGridData['Leader0Elbow'].Y, cGridData['Leader0Elbow'].Z)
                            #        cLeader.End = DB.XYZ(cGridData['Leader0End'].X, cGridData['Leader0End'].Y, cGridData['Leader0End'].Z)
                                        
                                    
                        else:
                            cAxis.HideBubbleInView(DB.DatumEnds.End0, cView)

                        if cGridData['EndBubble'] and cGridData['EndBubbleVisible']:
                            cAxis.ShowBubbleInView(DB.DatumEnds.End1, cView)
                            if 'Leader1Anchor' in cGridData:
                                if not cAxis.GetLeader(DB.DatumEnds.End1, cView):
                                    cLeader = cAxis.AddLeader(DB.DatumEnds.End1, cView)
                            #        cLeader = cAxis.GetLeader(DB.DatumEnds.End1, cView)
                                #        cLeader.Anchor = DB.XYZ(cGridData['Leader1Anchor'].X, cGridData['Leader1Anchor'].Y, cGridData['Leader1Anchor'].Z)
                                #        cLeader.Elbow = DB.XYZ(cGridData['Leader1Elbow'].X, cGridData['Leader1Elbow'].Y, cGridData['Leader1Elbow'].Z)
                                #        cLeader.End = DB.XYZ(cGridData['Leader1End'].X, cGridData['Leader1End'].Y, cGridData['Leader1End'].Z)
                                        
                        else:
                            cAxis.HideBubbleInView(DB.DatumEnds.End1, cView)
                    n += 1
            else:
                msg = 'Unknown grid \'{}\''.format(cAxis.Name)
                UI.TaskDialog.Show('py-ejs',msg)
        else:
            msg = 'Unknown element \'{}\''.format(cAxis.Name)
            UI.TaskDialog.Show('py-ejs',msg)
            
    if n<>1:
        msg = 'Restored placement for {} grids'.format(n)
    else:
        msg = 'Restored placement of the grid \'{}\''.format(cAxis.Name)
    UI.TaskDialog.Show('py-ejs',msg)

else:
    UI.TaskDialog.Show('py-ejs', 'View type \'{}\' not supported'.format(cView.ViewType))

