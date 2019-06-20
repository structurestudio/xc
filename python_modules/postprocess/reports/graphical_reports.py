# -*- coding: utf-8 -*-

from __future__ import print_function

__author__= "Ana Ortega (AO_O) "
__copyright__= "Copyright 2016, AO_O" 
__license__= "GPL"
__version__= "3.0"
__email__= " ana.Ortega@ciccp.es "

import xc_base
import geom
import xc
from postprocess.xcVtk.FE_model import vtk_FE_graphic
from postprocess.xcVtk.FE_model import Fields
from postprocess import utils_display
from postprocess.xcVtk import control_var_diagram as cvd
from postprocess.xcVtk import vtk_graphic_base
from postprocess.xcVtk.FE_model import quick_graphics as QGrph

class OuputUnits(object):
  '''Unit for the generation of graphic files report files.
  
  :ivar unitsScaleLoads: factor to apply to loads if we want to change
                   the units (defaults to 1).
  :ivar unitsLoads: text to especify the units in which loads are 
                   represented (defaults to 'units:[m,kN]')
  :ivar vectorScaleLoads: factor to apply to the vectors length in the 
                   representation of element loads (defaults to 1).
  :ivar vectorScalePointLoads: factor to apply to the vectors length in the 
                   representation of nodal loads (defaults to 1).
  :ivar unitsScaleDispl: factor to apply to displacements if we want to change
                   the units (defaults to 1).
  :ivar unitsDispl: text to especify the units in which displacements are 
                   represented (defaults to '[m]'
  :ivar scaleDispBeamIntForc: tuple (escN,escQ,escM) correponding to the scales
                   to apply to displays of, respectively, axial forces (N),
                   shear forces (Q) or bending moments (M) in beam elements
                   (defaults to (1.0,1.0,1.0))
  :ivar unitsScaleForc: factor to apply to internal forces if we want to change
                   the units (defaults to 1).
  :ivar unitsForc: text to especify the units in which forces are 
                   represented (defaults to '[kN/m]')
  :ivar unitsScaleMom: factor to apply to internal moments if we want to change
                   the units (defaults to 1).
  :ivar unitsMom:  text to especify the units in which bending moments are 
                   represented (defaults to '[kN.m/m]')
  '''

  def __init__(self):
    self.unitsScaleLoads=1.0
    self.unitsLoads='units:[m,kN]'
    self.vectorScaleLoads=1.0
    self.vectorScalePointLoads=1.0
    self.unitsScaleDispl=1.0
    self.unitsDispl='[m]'
    self.scaleDispBeamIntForc=(1.0,1.0,1.0)
    self.unitsScaleForc=1.0
    self.unitsForc='[kN/m]'
    self.unitsScaleMom=1.0
    self.unitsMom='[kN.m/m]'
    

class RecordLoadCaseDisp(OuputUnits):
  '''Generation of graphic files and adding to report-tex files for a load case
  
  :ivar loadCaseName:  name of the load case to be depicted
  :ivar loadCaseDescr: description text of the load case
  :ivar loadCaseExpr:  mathematical expression to define the load case (ex:
                   '1.0*GselfWeight+1.0*DeadLoad')
  :ivar setsToDispLoads: ordered list of sets of shell elements to display loads
  :ivar setsToDispBeamLoads: ordered list of sets of beam elements to display 
                   loads (defaults to [])
  :ivar compElLoad: component of load on beam elements to be represented
                   available components: 'axialComponent', 'transComponent', 
                   'transYComponent','transZComponent' (defaults to 'transComponent')
  :ivar multByElemAreaLoads: boolean value that must be True if we want to 
                   represent the total load on each element 
                   (=load multiplied by element area) and False if we 
                   are going to depict the value of the uniform load 
                   per unit area (defaults to False)
  :ivar listDspRot: ordered list of displacement or rotations to be displayed
                   available components: 'uX', 'uY', 'uZ', 'rotX', rotY', 'rotZ'
                   (defaults to ['uX', 'uY', 'uZ'])
  :ivar setsToDispDspRot: ordered list of sets of elements to display displacements 
                   or rotations
  :ivar listIntForc: ordered list of internal forces to be displayed
                   as scalar field over «shell» elements
                   available components: 'N1', 'N2', 'M1', 'M2', 'Q1', 'Q2'
                   (defaults to ['N1', 'N2', 'M1', 'M2', 'Q1', 'Q2'])
  :ivar setsToDispIntForc: ordered list of sets of elements  (of type «shell»)
                   to display internal forces
  :ivar listBeamIntForc: ordered list of internal forces to be displayed 
                 as diagrams on lines for «beam» elements
                 available components: 'N', 'My', 'Mz', 'Qy', 'Qz','T'
                 (defaults to ['N', 'My', 'Mz', 'Qy', 'Qz','T'])
  :ivar setsToDispBeamIntForc: ordered list of sets of elements (of type «beam»)
                    to display internal forces (defaults to [])
  :ivar cameraParameters: parameters that define the camera position,
                          zoom, etc.
  :ivar cameraParametersForBeams: parameters that define the camera position,
                          zoom, etc for displaying beam elements.
  '''

  def __init__(self,loadCaseName,loadCaseDescr,loadCaseExpr,setsToDispLoads,setsToDispDspRot,setsToDispIntForc):
    super(RecordLoadCaseDisp,self).__init__()
    self.loadCaseName=loadCaseName
    self.loadCaseDescr=loadCaseDescr
    self.loadCaseExpr=loadCaseExpr
    self.setsToDispLoads=setsToDispLoads
    self.setsToDispBeamLoads=[]
    self.compElLoad='transComponent'
    self.multByElemAreaLoads=False
    self.listDspRot=['uX', 'uY', 'uZ']
    self.setsToDispDspRot=setsToDispDspRot
    self.listIntForc=['N1', 'N2', 'M1', 'M2', 'Q1', 'Q2']
    self.setsToDispIntForc=setsToDispIntForc
    self.listBeamIntForc=['N', 'My', 'Mz', 'Qy', 'Qz','T']
    self.setsToDispBeamIntForc=[]
    self.cameraParameters= vtk_graphic_base.CameraParameters('XYZPos')
    self.cameraParametersBeams= vtk_graphic_base.CameraParameters('XYZPos')
    
  def loadReports(self,FEcase,pathGr,texFile,grWdt):
    '''Creates the graphics files of loads for the load case and insert them in
    a LaTex file
    
    :param FEcase:     finite element case 
    :param pathGr:     directory to place figures (ex: 'text/graphics/loads/')
    :param texFile:    laTex file where to include the graphics 
                       (e.g.:'text/report_loads.tex')
    :param grWdt:      width to be applied to graphics
    '''
    preprocessor=FEcase.getPreprocessor
    labl=self.loadCaseName
    for st in self.setsToDispLoads:
      grfname=pathGr+self.loadCaseName+st.name
      capt=self.loadCaseDescr + ', ' + st.description + ', '  + self.unitsLoads
      QGrph.displayLoad(preprocessor=preprocessor,setToDisplay=st,loadCaseNm=self.loadCaseName,unitsScale=self.unitsScaleLoads,vectorScale=self.vectorScaleLoads, multByElemArea=self.multByElemAreaLoads, viewDef= self.cameraParameters,caption= capt,fileName=grfname+'.jpg')
      QGrph.displayLoad(preprocessor=preprocessor,setToDisplay=st,loadCaseNm=self.loadCaseName,unitsScale=self.unitsScaleLoads,vectorScale=self.vectorScaleLoads, multByElemArea=self.multByElemAreaLoads, viewDef= self.cameraParameters,caption= capt,fileName=grfname+'.eps')
      insertGrInTex(texFile=texFile,grFileNm=grfname,grWdt=grWdt,capText=capt,labl=labl) 
    for st in self.setsToDispBeamLoads:
      grfname=pathGr+self.loadCaseName+st.name
      capt=self.loadCaseDescr + ', ' + st.description + ', '  + self.unitsLoads
      lcs=QGrph.QuickGraphics(FEcase)
      lcs.dispLoadCaseBeamEl(loadCaseName=self.loadCaseName,setToDisplay=st,fUnitConv=self.unitsScaleLoads,elLoadComp=self.compElLoad,elLoadScaleF=self.vectorScaleLoads,nodLoadScaleF=self.vectorScalePointLoads, viewDef= self.cameraParameters,caption= capt,fileName=grfname+'.jpg')
      lcs.dispLoadCaseBeamEl(loadCaseName=self.loadCaseName,setToDisplay=st,fUnitConv=self.unitsScaleLoads,elLoadComp=self.compElLoad,elLoadScaleF=self.vectorScaleLoads,nodLoadScaleF=self.vectorScalePointLoads, viewDef= self.cameraParameters,caption= capt,fileName=grfname+'.eps')
      insertGrInTex(texFile=texFile,grFileNm=grfname,grWdt=grWdt,capText=capt,labl=labl) 
    return

  def simplLCReports(self,FEproblem,pathGr,texFile,grWdt,capStdTexts):
    '''Creates the graphics files of displacements and internal forces 
     calculated for a simple load case and insert them in a LaTex file
    
    :param FEproblem:  finite element problem
    :param pathGr:     directory to place figures (ex: 'text/graphics/loads/')
    :param texFile:    laTex file where to include the graphics 
                       (e.g.:'text/report_loads.tex')
    :param grWdt:      width to be applied to graphics
    :param capStdTexts: dictionary with the standard captions.
    '''
    lcs=QGrph.QuickGraphics(FEproblem)
    #solve for load case
    lcs.solve(loadCaseName=self.loadCaseName,loadCaseExpr=self.loadCaseExpr)
    #Displacements and rotations displays
    for st in self.setsToDispDspRot:
        for arg in self.listDspRot:
            if arg[0]=='u':
                fcUn=self.unitsScaleDispl
                unDesc=self.unitsDispl
            else:
                fcUn=1.0
                unDesc=''
            grfname=pathGr+self.loadCaseName+st.name+arg
            lcs.displayDispRot(itemToDisp=arg,setToDisplay=st,fConvUnits=fcUn,unitDescription=unDesc, viewDef= self.cameraParameters,fileName=grfname+'.jpg')
            lcs.displayDispRot(itemToDisp=arg,setToDisplay=st,fConvUnits=fcUn,unitDescription=unDesc, viewDef= self.cameraParameters,fileName=grfname+'.eps')
            capt=self.loadCaseDescr + '. ' + st.description.capitalize() + ', ' + capStdTexts[arg] + ' ' + unDesc
            insertGrInTex(texFile=texFile,grFileNm=grfname,grWdt=grWdt,capText=capt)
    #Internal forces displays on sets of «shell» elements
    for st in self.setsToDispIntForc:
        for arg in self.listIntForc:
            if arg[0]=='M':
                fcUn=self.unitsScaleMom
                unDesc=self.unitsMom
            else:
                fcUn=self.unitsScaleForc
                unDesc=self.unitsForc
            grfname=pathGr+self.loadCaseName+st.name+arg
            lcs.displayIntForc(itemToDisp=arg,setToDisplay=st,fConvUnits= fcUn,unitDescription=unDesc, viewDef= self.cameraParameters,fileName=grfname+'.jpg')
            lcs.displayIntForc(itemToDisp=arg,setToDisplay=st,fConvUnits= fcUn,unitDescription=unDesc, viewDef= self.cameraParameters,fileName=grfname+'.eps')
            capt=self.loadCaseDescr + '. ' + st.description.capitalize() + ', ' + capStdTexts[arg] + ' ' + unDesc
            insertGrInTex(texFile=texFile,grFileNm=grfname,grWdt=grWdt,capText=capt)
    #Internal forces displays on sets of «beam» elements
    for st in self.setsToDispBeamIntForc:
        for arg in self.listBeamIntForc:
            if arg[0]=='M':
                fcUn=self.unitsScaleMom
                unDesc=self.unitsMom
                scaleFact=self.scaleDispBeamIntForc[2]
            else:
                fcUn=self.unitsScaleForc
                unDesc=self.unitsForc
                if arg[0]=='N':
                  scaleFact=self.scaleDispBeamIntForc[0]
                else:
                  scaleFact=self.scaleDispBeamIntForc[1]
            grfname=pathGr+self.loadCaseName+st.name+arg
            lcs.displayIntForcDiag(itemToDisp=arg,setToDisplay=st,fConvUnits= fcUn,scaleFactor=scaleFact,unitDescription=unDesc, viewDef= self.cameraParametersBeams,fileName=grfname+'.jpg')
            lcs.displayIntForcDiag(itemToDisp=arg,setToDisplay=st,fConvUnits= fcUn,scaleFactor=scaleFact,unitDescription=unDesc, viewDef= self.cameraParametersBeams,fileName=grfname+'.eps')
            capt=self.loadCaseDescr + '. ' + st.description.capitalize() + ', ' + capStdTexts[arg] + ' ' + unDesc
            insertGrInTex(texFile=texFile,grFileNm=grfname,grWdt=grWdt,capText=capt)
    texFile.write('\\clearpage\n')
    return

  def displayDispRot(self, fName= None):
    '''Displays load vectors on the set argument.

    :param setToDisplay: set of elements to be displayed (defaults to total set)
    :param fileName: full name of the graphic file to generate. Defaults to 
           ` None`, in this case it returns a console output graphic.,
    :param defFScale: factor to apply to current displacement of nodes 
                  so that the display position of each node equals to
                  the initial position plus its displacement multiplied
                  by this factor. (Defaults to 0.0, i.e. display of 
                  initial/undeformed shape)
    '''
    qg= QGrph.QuickGraphics()
    for st in self.setsToDispDspRot:
        for arg in self.listDspRot:
            if arg[0]=='u':
                fcUn= self.unitsScaleDispl
                unDesc= self.unitsDispl
            else:
                fcUn= 1.0
                unDesc=''
            qg.displayDispRot(itemToDisp=arg,setToDisplay=st,fConvUnits=fcUn,unitDescription=unDesc,viewDef= self.cameraParameters,fileName= fName)
    
  def displayLoad(self, setToDisplay, caption= None, fName= None, defFScale= 0.0):
    '''Displays load vectors on the set argument.

    :param setToDisplay: set of elements to be displayed (defaults to total set)
    :param caption: text to display in the graphic. Defaults to 
           ` None` in this case the text is the load case description
           and the units of the loads.
    :param fileName: full name of the graphic file to generate. Defaults to 
           ` None`, in this case it returns a console output graphic.,
    :param defFScale: factor to apply to current displacement of nodes 
                  so that the display position of each node equals to
                  the initial position plus its displacement multiplied
                  by this factor. (Defaults to 0.0, i.e. display of 
                  initial/undeformed shape)
    '''
    preprocessor= setToDisplay.getPreprocessor
    if(not caption):
      caption= 'load case: ' + self.loadCaseDescr + ', set: ' + setToDisplay.name + ', '  + self.unitsLoads
    QGrph.display_load(preprocessor,setToDisplay= setToDisplay,loadCaseNm=self.loadCaseName,unitsScale=self.unitsScaleLoads,vectorScale=self.vectorScaleLoads, multByElemArea=self.multByElemAreaLoads,viewDef= self.cameraParameters, caption= caption,fileName= fName,defFScale= defFScale)
      
  def displayIntForcDiag(self,itemToDisp,setToDisplay,fileName=None,defFScale=0.0):
    '''displays the component of internal forces in the set of entities as a 
     diagram over lines (i.e. appropiated for beam elements).

    :param itemToDisp: component of the internal forces 
      ('N', 'Qy' (or 'Vy'), 'Qz' (or 'Vz'), 'My', 'Mz', 'T') to be depicted 
    :param setToDisplay: set of entities (elements of type beam) to be 
      represented
    :param unitDescription: string like '[kN/m] or [kN m/m]'
    :param fileName:  name of the file to plot the graphic. Defaults to None,
                   in that case an screen display is generated
    :param defFScale: factor to apply to current displacement of nodes 
            so that the display position of each node equals to
            the initial position plus its displacement multiplied
            by this factor. (Defaults to 0.0, i.e. display of 
            initial/undeformed shape)
    '''
    if itemToDisp[0]=='M':
        fcUn=self.unitsScaleMom
        unDesc=self.unitsMom
        scaleFact=self.scaleDispBeamIntForc[2]
    else:
        fcUn=self.unitsScaleForc
        unDesc=self.unitsForc
        if itemToDisp[0]=='N':
          scaleFact=self.scaleDispBeamIntForc[0]
        else:
          scaleFact=self.scaleDispBeamIntForc[1]
    qg= QGrph.QuickGraphics()
    qg.displayIntForcDiag(itemToDisp= itemToDisp,setToDisplay= setToDisplay,fConvUnits= self.unitsScaleLoads,scaleFactor= scaleFact, unitDescription= unDesc, viewDef= self.cameraParameters, fileName= fileName, defFScale= defFScale)
    
  def dispLoadCaseBeamEl(self,setToDisplay,caption= None,fileName=None,defFScale=0.0):
    '''Display the loads applied on beam elements and nodes for a given load case

    :param setToDisplay:    set of beam elements to be represented
    :param caption:   caption for the graphic
    :param fileName:  name of the file to plot the graphic. Defaults to None,
                      in that case an screen display is generated
    :param defFScale: factor to apply to current displacement of nodes 
              so that the display position of each node equals to
              the initial position plus its displacement multiplied
              by this factor. (Defaults to 0.0, i.e. display of 
              initial/undeformed shape)
    '''
    qg= QGrph.QuickGraphics()
    if(not caption):
      caption= 'load case: ' + self.loadCaseDescr + ', set: ' + setToDisplay.name + ', '  + self.unitsLoads
    qg.dispLoadCaseBeamEl(loadCaseName=self.loadCaseName,setToDisplay=setToDisplay,fUnitConv=self.unitsScaleLoads,elLoadComp=self.compElLoad,elLoadScaleF=self.vectorScaleLoads,nodLoadScaleF=self.vectorScalePointLoads,viewDef= self.cameraParameters, caption= caption, fileName= fileName)

  def displayLoadOnSets(self, caption= None, fName= None, defFScale= 0.0):
    '''Displays load vectors for each of the sets in self.setsToDispLoads

    :param caption: text to display in the graphic. Defaults to 
           ` None` in this case the text is the load case description
           and the units of the loads.
    :param fileName: full name of the graphic file to generate. Defaults to 
           ` None`, in this case it returns a console output graphic.,
    :param defFScale: factor to apply to current displacement of nodes 
                  so that the display position of each node equals to
                  the initial position plus its displacement multiplied
                  by this factor. (Defaults to 0.0, i.e. display of 
                  initial/undeformed shape)
    '''
    for st in self.setsToDispLoads:
      self.displayLoad(setToDisplay= st,caption= caption,fName= fName,defFScale= defFScale)
    for st in self.setsToDispBeamLoads:
      self.dispLoadCaseBeamEl(setToDisplay=st, fileName= fName, defFScale= defFScale)

def checksReports(limitStateLabel,setsShEl,argsShEl,capTexts,pathGr,texReportFile,grWdt,setsBmElView=[],argsBmElScale=[]):
    '''Create a LaTeX report including the desired graphical results obtained
     in the verification of a limit state.

    :param limitStateLabel: limit state
    :param setsShEl:   Ordered list of sets of shell elements (defined in 
                       model_data.py as instances of utils_display.setToDisplay)
                       to be included in the report
    :param argsShEl:   Ordered list of arguments to be included in the report   
                       for shell elements
    :param capTexts:  dictionary from wich to read the texts for captions
    :param pathGr:     width to be applied to graphics 
    :param texReportFile: laTex file where to include the graphics
    :param grWdt:      width of the graphics for the tex file
    :param setsBmView: Ordered list of lists [set of beam elements, view to 
                       represent this set] to be included in the report. 
                       The sets have been defined in model_data.py 
                       as instances of utils_display.setToDisplay and the 
                       possible views are: 'XYZPos','XNeg','XPos','YNeg','YPos',
                       'ZNeg','ZPos'  (defaults to 'XYZPos')
    :param argsShEl:   Ordered list of lists [arguments, scale to represent the 
                       argument] to be included in the report for beam elements
    '''
    report=open(texReportFile,'w')    #report latex file
    dfDisp= vtk_FE_graphic.RecordDefDisplayEF()
    for st in setsShEl:
        for arg in argsShEl:
            attributeName= limitStateLabel + 'Sect1'
            field= Fields.getScalarFieldFromControlVar(attributeName,arg,st,None,1.0)
            capt=capTexts[limitStateLabel] + ', ' + capTexts[arg] + '. '+ st.description.capitalize() + ', ' + 'section 1'
            grFileNm=pathGr+st.name+arg+'Sect1'
            field.display(defDisplay=dfDisp,caption=capt,fName=grFileNm+'.jpg')
            insertGrInTex(texFile=report,grFileNm=grFileNm,grWdt=grWdt,capText=capt)

            attributeName= limitStateLabel + 'Sect2'
            field= Fields.getScalarFieldFromControlVar(attributeName,arg,st,None,1.0)
            capt=capTexts[limitStateLabel] + ', ' + capTexts[arg] + '. '+ st.description.capitalize() + ', ' + 'section 2'
            grFileNm=pathGr+st.name+arg+'Sect2'
            field.display(defDisplay=dfDisp,caption=capt,fName=grFileNm+'.jpg')
            insertGrInTex(texFile=report,grFileNm=grFileNm,grWdt=grWdt,capText=capt)
    for stV in setsBmElView:
        for argS in argsBmElScale:
            diagram= cvd.ControlVarDiagram(scaleFactor=argS[1],fUnitConv=1,sets=[stV[0]],attributeName= limitStateLabel,component= argS[0])
            diagram.addDiagram()
            dfDisp.cameraParameters= vtk_graphic_base.CameraParameters(stV[1])
            dfDisp.setupGrid(stV[0])
            dfDisp.defineMeshScene(None)
            dfDisp.appendDiagram(diagram)
            capt= capTexts[limitStateLabel] + ', ' + capTexts[argS[0]] + '. '+ stV[0].description.capitalize() + ', ' + 'section 1'
            grFileNm=pathGr+stV[0].name+argS[0]
            dfDisp.displayScene(caption=capt,fName=grFileNm+'.jpg')
            insertGrInTex(texFile=report,grFileNm=grFileNm,grWdt=grWdt,capText=capt)
    report.close()
    return

def insertGrInTex(texFile,grFileNm,grWdt,capText,labl=''):
    '''Include a graphic in a LaTeX file.

    :param texFile:    laTex file where to include the graphics 
                       (e.g.\:'text/report_loads.tex')
    :param grFileNm:   name of the graphic file with path and without extension
    :param grWdt:      width to be applied to graphics
    :param capText:    text for the caption
    :param labl:       label
    '''
    texFile.write('\\begin{figure}\n')
    texFile.write('\\begin{center}\n')
    texFile.write('\\includegraphics[width='+grWdt+']{'+grFileNm+'}\n')
    texFile.write('\\caption{'+capText+'}\n')
    if labl<>'':
      texFile.write('\\label{'+labl+'}\n')
    texFile.write('\\end{center}\n')
    texFile.write('\\end{figure}\n')
    return
  
def getRecordLoadCaseDispFromLoadPattern(loadPattern, unitsScaleLoads= 1e-3, unitsScaleDispl= 1e-3, setsToDispLoads= None, setsToDispDspRot= None, setsToDispIntForc= None):
  domain= loadPattern.getDomain # Not always set.
  if(domain):
      xcTotalSet= domain.getPreprocessor.getSets.getSet("total")
      if(not setsToDispLoads):
        setsToDispLoads= [xcTotalSet]
      if(not setsToDispDspRot):
        setsToDispDspRot= [xcTotalSet]
      if(not setsToDispIntForc):
        setsToDispIntForc= [xcTotalSet]
  name= loadPattern.name
  retval= RecordLoadCaseDisp(name,loadPattern.description,'1.0*'+name,setsToDispLoads,setsToDispDspRot,setsToDispIntForc)
  retval.unitsScaleLoads=1e-3
  retval.unitsScaleForc=1e-3
  retval.unitsScaleMom=1e-3
  retval.unitsScaleDispl=1e3
  retval.unitsDispl='[mm]'
  return retval
