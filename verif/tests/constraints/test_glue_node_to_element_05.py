# -*- coding: utf-8 -*-
# home made test

E= 2.1e6 # Young modulus of the steel en kg/cm2.
nu= 0.3 # Poisson's ratio.
h= 0.1 # Espesor.
dens= 1.33 # Densidad kg/m2.

import xc_base
import geom
import xc
from model import predefined_spaces
from materials import typical_materials
import math
from model import fix_node_6dof
from model import nodalReactions
from solution import predefined_solutions

prueba= xc.ProblemaEF()
preprocessor=  prueba.getPreprocessor
nodes= preprocessor.getNodeLoader


p1= geom.Pos3d(0,0,0)
p2= geom.Pos3d(1,0,0)
p3= geom.Pos3d(1,1,0)
p4= geom.Pos3d(0,1,0)

# Problem type
predefined_spaces.gdls_resist_materiales3D(nodes)
n1= nodes.newNodeXYZ(p1.x,p1.y,p1.z)
n2= nodes.newNodeXYZ(p2.x,p2.y,p2.z)
n3= nodes.newNodeXYZ(p3.x,p3.y,p3.z)
n4= nodes.newNodeXYZ(p4.x,p4.y,p4.z)

p10= geom.Pos3d(0.5,0.5,0.0)
n10= nodes.newNodeXYZ(p10.x,p10.y,p10.z)

# Materials definition
memb1= typical_materials.defElasticMembranePlateSection(preprocessor, "memb1",E,nu,dens,h)
elementos= preprocessor.getElementLoader
elementos.defaultMaterial= "memb1"
elem= elementos.newElement("shell_mitc4",xc.ID([n1.tag,n2.tag,n3.tag,n4.tag]))

# Constraints
coacciones= preprocessor.getConstraintLoader
fix_node_6dof.Nodo6DOFGirosLibres(coacciones, n1.tag)
fix_node_6dof.Nodo6DOFGirosLibres(coacciones, n2.tag)
fix_node_6dof.Nodo6DOFGirosLibres(coacciones, n3.tag)
fix_node_6dof.Nodo6DOFGirosLibres(coacciones, n4.tag)
#fix_node_6dof.fixNode6DOF(coacciones, 1)
#fix_node_6dof.fixNode6DOF(coacciones, 2)
#fix_node_6dof.fixNode6DOF(coacciones, 3)
#fix_node_6dof.fixNode6DOF(coacciones, 4)

#Glued node.
gluedDOFs= [0,1,2,3,4,5]
loadOnDOFs= [0,0,0,0,0,0]
for i in range(0,6):
  if i not in gluedDOFs:
    coacciones.newSPConstraint(n10.tag,i,0.0)
  else:
    loadOnDOFs[i]= -1000.0

glue= coacciones.newGlueNodeToElement(n10,elem,xc.ID(gluedDOFs))

# Loads definition
cargas= preprocessor.getLoadLoader

casos= cargas.getLoadPatterns

#Load modulation.
ts= casos.newTimeSeries("constant_ts","ts")
casos.currentTimeSeries= "ts"
#Load case definition
lp0= casos.newLoadPattern("default","0")
lp0.newNodalLoad(n10.tag,xc.Vector(loadOnDOFs))
#We add the load case to domain.
casos.addToDomain("0")

# Solution
prbSolver= predefined_solutions.SolutionProcedure()
analisis= prbSolver.simpleTransformationStaticLinear(prueba)
result= analisis.analyze(1)

nodes.calculateNodalReactions(False)

reactionNode10= n10.getReaction
ratio1= reactionNode10.Norm()
svdReactionNodes= nodalReactions.getReactionFromNodes(nodes,"UVWRxRyRz",elem.getNodes.getExternalNodes)
actionNode10= xc.Vector(loadOnDOFs)
actionNode10Norm= actionNode10.Norm()
svdAction= nodalReactions.getSVDfromVDesliz("UVWRxRyRz",n10.get3dCoo,actionNode10)
svdResid= svdReactionNodes+svdAction
ratio2= svdResid.getResultante().getModulo()/actionNode10Norm
ratio3= svdResid.getMomento().getModulo()/actionNode10Norm

# print "svdAction= ", svdAction
# print "svdReactionNodes= ", svdReactionNodes
# print "svdResid= ", svdResid
# print "ratio1= ", ratio1
# print "ratio2= ", ratio2
# print "ratio3= ", ratio3
# print "RN2= ", RN2
# print "RN3= ", RN3
# print "RN4= ", RN4

import os
fname= os.path.basename(__file__)
if (abs(ratio1)<1e-10) & (abs(ratio2)<1e-9) & (abs(ratio3)<1e-9) & (result==0):
  print "test ",fname,": ok."
else:
  print "test ",fname,": ERROR."