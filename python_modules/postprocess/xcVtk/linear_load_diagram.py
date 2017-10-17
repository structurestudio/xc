 # -*- coding: utf-8 -*-

''' Display of loads over linear elements. '''

import geom
import vtk
from postprocess.xcVtk import colored_diagram as cd
from miscUtils import LogMessages as lmsg

class LinearLoadDiagram(cd.ColoredDiagram):
  '''Draws a load over a linear element (qx,qy,qz,...)'''
  def __init__(self,scale,fUnitConv,loadPatternName,component):
    super(LinearLoadDiagram,self).__init__(scale,fUnitConv)
    print loadPatternName
    self.lpName= loadPatternName
    self.component= component

  def dumpElementalLoads(self,preprocessor,lp,indxDiagram):
    ''' Iterate over loaded elements dumping its loads into the graphic.'''
    lIter= lp.loads.getElementalLoadIter
    eLoad= lIter.next()
    while(eLoad):
      tags= eLoad.elementTags
      for i in range(0,len(tags)):
        eTag= tags[i]
        elem= preprocessor.getElementLoader.getElement(eTag)
        if(self.component=='axialComponent'):
          self.vDir= elem.getJVector3d(True)
          indxDiagram= self.agregaDatosADiagrama(elem,indxDiagram,eLoad.axialComponent,eLoad.axialComponent)
        elif(self.component=='transComponent'):
          self.vDir= elem.getJVector3d(True) # initialGeometry= True  
          indxDiagram= self.agregaDatosADiagrama(elem,indxDiagram,eLoad.transComponent,eLoad.transComponent)
        elif(self.component=='transYComponent'):
          self.vDir= elem.getJVector3d(True) # initialGeometry= True  
          indxDiagram= self.agregaDatosADiagrama(elem,indxDiagram,eLoad.transYComponent,eLoad.transYComponent)
        elif(self.component=='transZComponent'):
          self.vDir= elem.getKVector3d(True) # initialGeometry= True  
          indxDiagram= self.agregaDatosADiagrama(elem,indxDiagram,eLoad.transZComponent,eLoad.transZComponent)
        else:
          lmsg.error("LinearLoadDiagram :'"+self.component+"' unknown.")        
      eLoad= lIter.next()
  def dumpLoads(self, preprocessor, indxDiagram):
    preprocessor.resetLoadCase()
    loadPatterns= preprocessor.getLoadLoader.getLoadPatterns
    loadPatterns.addToDomain(self.lpName)
    lp= loadPatterns[self.lpName]
    #Iterate over loaded elements.
    if(lp):
      self.dumpElementalLoads(preprocessor,lp,indxDiagram)
    else:
      lmsg.error('load pattern: '+self.lpName+' not found.')

  def addDiagram(self,preprocessor):
    self.creaEstrucDatosDiagrama()
    self.creaLookUpTable()
    self.creaActorDiagrama()

    indxDiagram= 0
    self.dumpLoads(preprocessor,indxDiagram)

    self.updateLookUpTable()
    self.updateActorDiagrama()
