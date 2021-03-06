# -*- coding: utf-8 -*-

__author__= "Luis C. Pérez Tato (LCPT)"
__copyright__= "Copyright 2016,LCPT"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com"

import math
from materials.sections import internal_forces
from misc_utils import log_messages as lmsg

def getInternalForcesDict(nmbComb, elems):
    '''Creates a dictionary with the element's internal forces.

    :param nmbComb: combination name.
    :param elems: element set.
    :param fDesc: file descriptor to write internal forces on.
    '''
    combInternalForcesDict= dict()
    outDict= dict()
    combInternalForcesDict[nmbComb]= outDict
    for e in elems:
        elemDict= dict()
        outDict[e.tag]= elemDict
        elementType= e.type()
        elemDict['type']= elementType
        if('Shell' in elementType):
            internalForces= internal_forces.ShellMaterialInternalForces()
            internalForces.setFromAverageInShellElement(e)
            internalForces= internalForces.getWoodArmer()
            sz= len(internalForces)
            internalForcesDict= dict()
            for i in range(0,sz):
                nForceDict= dict()
                force= internalForces[i]
                internalForcesDict[i]= force.getDict()
            elemDict['internalForces']= internalForcesDict
        elif('Beam2d' in elementType):
            e.getResistingForce()
            internalForcesDict= dict()
            # Internal forces of the bar. 
            N1= 0.0; M1= 0.0; V1= 0.0
            N2= 0.0; M2= 0.0; V2= 0.0
            axialForces= e.getValuesAtNodes('N')
            if(len(axialForces)>1): # 'N' found.
                N1= axialForces[0]
                N2= axialForces[1]
            bending= e.getValuesAtNodes('M')
            if(len(bending)>1): # 'M' found.
                M1= bending[0]
                M2= bending[1]
            shear= e.getValuesAtNodes('V')
            if(len(shear)>1): # 'V' found.
                V1= shear[0]
                V2= shear[1]
            internalForces= internal_forces.CrossSectionInternalForces(N1,V1,0.0,0.0,0.0,M1) 
            internalForcesDict[0]= internalForces.getDict()
            internalForces= internal_forces.CrossSectionInternalForces(N2,V2,0.0,0.0,0.0,M2) # Internal forces at the end of the bar.
            internalForcesDict[1]= internalForces.getDict()
            elemDict['internalForces']= internalForcesDict
        elif('Beam' in elementType):
            e.getResistingForce()
            internalForcesDict= dict()
            N1= 0.0; My1= 0.0; Mz1= 0.0; Vy1= 0.0;
            N2= 0.0; My2= 0.0; Mz2= 0.0; Vy2= 0.0;
            axialForces= e.getValuesAtNodes('N')
            if(len(axialForces)>1): # 'N' found.
                N1= axialForces[0]
                N2= axialForces[1]
            shearY= e.getValuesAtNodes('Vy')
            if(len(shearY)>1): # 'Vy' found.
                Vy1= shearY[0]
                Vy2= shearY[1]
            shearZ= e.getValuesAtNodes('Vz')
            if(len(shearZ)>1): # 'Vz' found.
                Vz1= shearZ[0]
                Vz2= shearZ[1]
            torque= e.getValuesAtNodes('T')
            if(len(torque)>1): # 'T' found.
                T1= torque[0]
                T2= torque[1]
            bendingY= e.getValuesAtNodes('My')
            if(len(bendingY)>1): # 'My' found.
                My1= bendingY[0]
                My2= bendingY[1]
            bendingZ= e.getValuesAtNodes('Mz')
            if(len(bendingZ)>1): # 'Mz' found.
                Mz1= bendingZ[0]
                Mz2= bendingZ[1]
            internalForces= internal_forces.CrossSectionInternalForces(N1,Vy1,Vz1,T1,My1,Mz1) # Internal forces at the origin of the bar.
            internalForcesDict[0]= internalForces.getDict()
            if e.hasProp('chiLT'):   #steel beam
                internalForcesDict[0]['chiLT']= e.getProp('chiLT')
            if e.hasProp('chiN'):   #steel beam
                internalForcesDict[0]['chiN']= e.getProp('chiN')
            internalForces= internal_forces.CrossSectionInternalForces(N2,Vy2,Vz2,T2,My2,Mz2) # Internal forces at the end of the bar.
            internalForcesDict[1]= internalForces.getDict()
            if e.hasProp('chiLT'):
                internalForcesDict[1]['chiLT']= e.getProp('chiLT')
            if e.hasProp('chiN'):
                internalForcesDict[1]['chiN']= e.getProp('chiN')
            elemDict['internalForces']= internalForcesDict
        elif('Truss' in elementType):
            e.getResistingForce()
            internalForcesDict= dict()
            N1= 0.0
            N2= 0.0
            axialForces= e.getValuesAtNodes('N')
            if(len(axialForces)>1): # 'N' found.
                N1= axialForces[0]
                N2= axialForces[1]
            internalForces= internal_forces.CrossSectionInternalForces(N1) # Internal forces at the origin of the bar.
            internalForcesDict[0]= internalForces.getDict()
            if e.hasProp('chiLT'):   #steel beam
                internalForcesDict[0]['chiLT']= e.getProp('chiLT')
            if e.hasProp('chiN'):   #steel beam
                internalForcesDict[0]['chiN']= e.getProp('chiN')
            internalForces= internal_forces.CrossSectionInternalForces(N2) # Internal forces at the end of the bar.
            internalForcesDict[1]= internalForces.getDict()
            if e.hasProp('chiLT'):
                internalForcesDict[1]['chiLT']= e.getProp('chiLT')
            if e.hasProp('chiN'):
                internalForcesDict[1]['chiN']= e.getProp('chiN')
            elemDict['internalForces']= internalForcesDict
        elif('ZeroLength' in elementType):
          lmsg.warning("exportInternalForces for element type: '"+elementType+"' not implemented.")
        else:
          lmsg.error("exportInternalForces error; element type: '"+elementType+"' unknown.")
    return combInternalForcesDict

def exportInternalForces(nmbComb, elems, fDesc):
    '''Writes a comma separated values file with the element's internal forces.

    :param nmbComb: combination name.
    :param elems: element set.
    :param fDesc: file descriptor to write internal forces on.'''
    errMsg= 'exportInternalForces deprecated use getInternalForcesDict'
    errMsg+= 'with apropriate arguments'
    for e in elems:
        elementType= e.type()
        if('Shell' in elementType):
          internalForces= internal_forces.ShellMaterialInternalForces()
          internalForces.setFromAverageInShellElement(e)
          forcesOnNodes= internalForces.getWoodArmer()
          sz= len(forcesOnNodes)
          for i in range(0,sz):
            force= forcesOnNodes[i]
            outStr= nmbComb+", "+str(e.tag)+", "+str(i)+", "+force.getCSVString()+'\n'
            fDesc.write(outStr)
        elif('Beam2d' in elementType):
            e.getResistingForce()
            # Internal forces at the origin of the bar. 
            N1= 0.0; M1= 0.0; V1= 0.0
            N2= 0.0; M2= 0.0; V2= 0.0
            axialForces= e.getValuesAtNodes('N')
            if(len(axialForces)>1): # 'N' found.
                N1= axialForces[0]
                N2= axialForces[1]
            bending= e.getValuesAtNodes('M')
            if(len(bending)>1): # 'M' found.
                M1= bending[0]
                M2= bending[1]
            shear= e.getValuesAtNodes('V')
            if(len(shear)>1): # 'V' found.
                V1= shear[0]
                V2= shear[1]
            internalForces= internal_forces.CrossSectionInternalForces(N1,V1,0.0,0.0,0.0,M1) 
            fDesc.write(nmbComb+", "+str(e.tag)+", 0, "+internalForces.getCSVString()+'\n')
            internalForces= internal_forces.CrossSectionInternalForces(N2,V2,0.0,0.0,0.0,M2) # Internal forces at the end of the bar.
            fDesc.write(nmbComb+", "+str(e.tag)+", 1, "+internalForces.getCSVString()+'\n')
        elif('Beam' in elementType):
            e.getResistingForce()
            N1= 0.0; Vy1= 0.0; Vz1= 0.0; T1= 0.0; My1= 0.0; Mz1= 0.0
            N2= 0.0; Vy2= 0.0; Vz2= 0.0; T2= 0.0; My2= 0.0; Mz2= 0.0 
            axialForces= e.getValuesAtNodes('N')
            if(len(axialForces)>1): # 'N' found.
                N1= axialForces[0]
                N2= axialForces[1]
            shearY= e.getValuesAtNodes('Vy')
            if(len(shearY)>1): # 'Vy' found.
                Vy1= shearY[0]
                Vy2= shearY[1]
            shearZ= e.getValuesAtNodes('Vz')
            if(len(shearZ)>1): # 'Vz' found.
                Vz1= shearZ[0]
                Vz2= shearZ[1]
            torque= e.getValuesAtNodes('T')
            if(len(torque)>1): # 'T' found.
                T1= torque[0]
                T2= torque[1]
            bendingY= e.getValuesAtNodes('My')
            if(len(bendingY)>1): # 'My' found.
                My1= bendingY[0]
                My2= bendingY[1]
            bendingZ= e.getValuesAtNodes('Mz')
            if(len(bendingZ)>1): # 'Mz' found.
                Mz1= bendingZ[0]
                Mz2= bendingZ[1]
            internalForces= internal_forces.CrossSectionInternalForces(N1,Vy1,Vz1,T1,My1,Mz1) # Internal forces at the origin of the bar.
            if e.hasProp('chiLT'):   #steel beam
                fDesc.write(nmbComb+", "+str(e.tag)+", 0, "+internalForces.getCSVString()+" , "+str(e.getProp('chiLT'))+'\n')
            else:
                fDesc.write(nmbComb+", "+str(e.tag)+", 0, "+internalForces.getCSVString()+'\n')
            internalForces= internal_forces.CrossSectionInternalForces(N2,Vy2,Vz2,T2,My2,Mz2) # Internal forces at the end of the bar.
            if e.hasProp('chiLT'):
                fDesc.write(nmbComb+", "+str(e.tag)+", 1, "+internalForces.getCSVString()+" , " + str(e.getProp('chiLT'))+'\n')
            else:
                fDesc.write(nmbComb+", "+str(e.tag)+", 1, "+internalForces.getCSVString()+'\n')
        elif('Truss' in elementType):
            e.getResistingForce()
            N1= 0.0
            N2= 0.0
            axialForces= e.getValuesAtNodes('N')
            if(len(axialForces)>1): # 'N' found.
                N1= axialForces[0]
                N2= axialForces[1]
            internalForces= internal_forces.CrossSectionInternalForces(N1) # Internal forces at the origin of the bar.
            if e.hasProp('chiLT'):   #steel beam
                fDesc.write(nmbComb+", "+str(e.tag)+", 0, "+internalForces.getCSVString()+" , "+str(e.getProp('chiLT'))+'\n')
            else:
                fDesc.write(nmbComb+", "+str(e.tag)+", 0, "+internalForces.getCSVString()+'\n')
            internalForces= internal_forces.CrossSectionInternalForces(N2) # Internal forces at the end of the bar.
            if e.hasProp('chiLT'):
                fDesc.write(nmbComb+", "+str(e.tag)+", 1, "+internalForces.getCSVString()+" , " + str(e.getProp('chiLT'))+'\n')
            else:
                fDesc.write(nmbComb+", "+str(e.tag)+", 1, "+internalForces.getCSVString()+'\n')
        elif('ZeroLength' in elementType):
            lmsg.warning("exportInternalForces for element type: '"+elementType+"' not implemented.")
        else:
            lmsg.error("exportInternalForces error; element type: '"+elementType+"' unknown.")
      

def exportShellInternalForces(nmbComb, elems, fDesc,fConv= 1.0):
    '''Writes a comma separated values file with the element's internal forces.'''
    errMsg= 'exportShellInternalForces deprecated use exportInternalForces'
    errMsg+= 'with apropriate arguments'
    lmsg.error(errMsg)
    internalForces= internal_forces.ShellMaterialInternalForces()
    for e in elems:
      internalForces.setFromAverageInShellElement(e)
      strEsf= internalForces.getCSVString()
      forcesOnNodes= internalForces.getWoodArmer()
      sz= len(forcesOnNodes)
      for i in range(0,sz):
        force= forcesOnNodes[i]
        outStr= nmbComb+", "+str(e.tag)+", "+str(i)+", "+force.getCSVString()+'\n'
        fDesc.write(outStr)

def exportaEsfuerzosShellSet(preprocessor,nmbComb, st, fName):
    '''Writes a comma separated values file with the element's internal forces.'''
    errMsg= 'exportaEsfuerzosShellSet deprecated use exportInternalForces'
    errMsg+= 'with apropriate arguments'
    lmsg.error(errMsg)
    elems= st.elements
    exportShellInternalForces(nmbComb,elems,fName)

def exportBeamInternalForces(nmbComb, elems, fName):
    '''Writes a comma separated values file with the element's internal forces.'''
    for e in elems:
        e.getResistingForce()
        N1= 0.0; Vy1= 0.0; Vz1= 0.0; T1= 0.0; My1= 0.0; Mz1= 0.0
        N2= 0.0; Vy2= 0.0; Vz2= 0.0; T2= 0.0; My2= 0.0; Mz2= 0.0; 
        axialForces= e.getValuesAtNodes('N')
        if(len(axialForces)>1): # 'N' found.
            N1= axialForces[0]
            N2= axialForces[1]
        shearY= e.getValuesAtNodes('Vy')
        if(len(shearY)>1): # 'Vy' found.
            Vy1= shearY[0]
            Vy2= shearY[1]
        shearZ= e.getValuesAtNodes('Vz')
        if(len(shearZ)>1): # 'Vz' found.
            Vz1= shearZ[0]
            Vz2= shearZ[1]
        torque= e.getValuesAtNodes('T')
        if(len(torque)>1): # 'T' found.
            T1= torque[0]
            T2= torque[1]
        bendingY= e.getValuesAtNodes('My')
        if(len(bendingY)>1): # 'My' found.
            My1= bendingY[0]
            My2= bendingY[1]
        bendingZ= e.getValuesAtNodes('Mz')
        if(len(bendingZ)>1): # 'Mz' found.
            Mz1= bendingZ[0]
            Mz2= bendingZ[1]
        internalForces= internal_forces.CrossSectionInternalForces(N1,Vy1,Vz1,T1,My1,Mz1) # Internal forces at the origin of the bar.
        fName.write(nmbComb+", "+str(e.tag*10+1)+","+internalForces.getCSVString())
        internalForces= internal_forces.CrossSectionInternalForces(N2,Vy2,Vz2,T2,My2,Mz2) # Internal forces at the end of the bar.
        fName.write(nmbComb+", "+str(e.tag*10+2)+","+internalForces.getCSVString())
