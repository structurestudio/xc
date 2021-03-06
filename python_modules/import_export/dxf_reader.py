# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function

__author__= "Luis C. Pérez Tato (LCPT) and Ana Ortega (AO_O)"
__copyright__= "Copyright 2015, LCPT and AO_O"
__license__= "GPL"
__version__= "3.0"
__email__= "l.pereztato@gmail.com" "ana.ortega.ort@gmail.com"

import math
import ezdxf
import xc_base
import geom
import xc
import re
from scipy.spatial.distance import cdist
from import_export import block_topology_entities as bte
from misc_utils import log_messages as lmsg

class FloatList(list):
    '''List of floats that are more than
       "tol" apart.
    '''
    def __init__(self,tol= .01):
      super(FloatList,self).__init__()
      self.tol= tol
    def append(self,num):
        dMin= 1e23
        for v in self:
            dMin= min(abs(num-v), dMin)
        if(dMin>self.tol):
            super(FloatList,self).append(num)


def get_candidate_2Dquads(sisRef, points, tol):
    '''Return candidate quads in 2D.'''
    # Compute relative coordinates.
    x_i= FloatList(tol)
    y_i= FloatList(tol)
    for p in points:
        pRel= sisRef.getPosLocal(geom.Pos3d(p[0],p[1],p[2]))
        x_i.append(pRel[0])
        y_i.append(pRel[1])
    x_i.sort()
    nx= len(x_i)
    y_i.sort()
    ny= len(y_i)
    # Create candidate surfaces.
    candidates= list()
    for i in range(0,nx-1):
        for j in range(0, ny-1):
            x= x_i[i]; y= y_i[j]
            p1= geom.Pos2d(x,y)
            x= x_i[i+1]; y= y_i[j]
            p2= geom.Pos2d(x,y)
            x= x_i[i+1]; y= y_i[j+1]
            p3= geom.Pos2d(x,y)
            x= x_i[i]; y= y_i[j+1]
            p4= geom.Pos2d(x,y)
            face= geom.Polygon2d()
            face.appendVertex(p1)
            face.appendVertex(p2)
            face.appendVertex(p3)
            face.appendVertex(p4)
            candidates.append(face)
    return candidates

def quads2d_to_global_coordinates(sisRef, selected_quads):
    '''Convert the quads from 2D to 3D.'''
    retval= list()
    for face in selected_quads:
        vList= list()
        vertices= face.getVertices()
        for v in vertices:
            vList.append(sisRef.getPosGlobal(geom.Pos3d(v.x,v.y,0.0)))
        retval.append(vList)
    return retval
    
def get_polygon_axis(points, tol):
    '''Compute the polygon axis on the assumption that
       they all the sides are orthogonal.'''
    pline= geom.Polyline3d()
    for p in points:
        pline.appendVertex(geom.Pos3d(p[0],p[1],p[2]))
    pline.simplify(tol)
    pt0= pline[1]
    pt1= pline[2]
    pt2= pline[3]
    v1= pt0-pt1
    v2= pt2-pt1
    return geom.Ref3d3d(pt1,v1,v2)    
    
def decompose_polyline(polyline, tol= .01):
    '''Return the quadrilateral surfaces that
       compose the polyline.
    '''
    retval= list()
    if((len(polyline)>2) and polyline.is_closed):
        # Compute the local axis.
        points= list()
        for i, pt in enumerat(i,polyline.points()):
            points.append([pt[0],pt[1],pt[2]])            
        sisRef= get_polygon_axis(points,tol)

        # Create candidate surfaces.
        candidates= get_candidate_2Dquads(sisRef, points, tol)

        # Create polygon in local coordinates.
        polygon= geom.Polygon2d()
        for pt in polyline:
            ptLocal= sisRef.getPosLocal(geom.Pos3d(pt[0],pt[1],pt[2]))
            polygon.appendVertex(geom.Pos2d(ptLocal.x,ptLocal.y))

        # Select surfaces inside polygon.
        selected= list()
        for face in candidates:
            c= face.getCenterOfMass()
            if(polygon.In(c,tol/5.0)):
                selected.append(face)
        retval= quads2d_to_global_coordinates(sisRef, selected)

    return retval

def get_polyface_points_axis(polyface_points):
    ''' Return the axis for the polyface.'''
    p= geom.Plane3d()
    p.linearLeastSquaresFitting(polyface_points)
    global_z= geom.Vector3d(0.0,0.0,1.0)
    local_z= p.getNormal()
    angle= local_z.getAngle(global_z)
    local_y= global_z
    global_y= geom.Vector3d(0.0,1.0,0.0)    
    if(abs(angle)<1e-3 or abs(angle-math.pi)<1e-3):
        local_y= global_y
    local_x= local_y.cross(local_z)
    local_y= local_z.cross(local_x)
    org= polyface_points[0]
    return geom.Ref3d3d(org,local_x,local_y)    
    
def decompose_polyface(polyface, tol= .01):
    '''Return the quadrilateral surfaces that
       compose the polyface.
    '''
    lmsg.error('decompose_polyface needs debugging after migration to ezdxf')
    # Compute the reference axis.
    points= geom.PolyPos3d()
    for face in polyface.faces():
        for v in face[0:3]:
            pt= v.dxf.location
            points.append(geom.Pos3d(pt[0],pt[1],pt[2]))
    sisRef= get_polyface_points_axis(points)

    # Create candidate surfaces.
    candidates= get_candidate_2Dquads(sisRef,points, tol)

    # Create polygons in local coordinates.
    polyfaces2d= list()
    for face in polyface.faces():
        polygon= geom.Polygon2d()
        for v in face[0:3]:
            pt= v.dxf.location
            ptLocal= sisRef.getPosLocal(geom.Pos3d(pt[0],pt[1],pt[2]))
            polygon.appendVertex(geom.Pos2d(ptLocal.x,ptLocal.y))
        polyfaces2d.append(polygon)
    # Select surfaces inside polyface.
    selected= list()
    for face in candidates:
        c= face.getCenterOfMass()
        for polyface in polyfaces2d:
            if(polyface.In(c,tol/5.0)):
                selected.append(face)
                break
    return quads2d_to_global_coordinates(sisRef, selected)

def layerToImport(layerName,namesToImport):
    '''Return true if the layer name matches one of the regular expressions
       contained in the second argument.

       :param layerName: name of the layer.
       :param namesToImport: list of regular expressions to be tested.
    '''
    for regExp in namesToImport:
        if(re.match(regExp,layerName)):
            return True
    return False

def get_extended_data(obj, appName= 'XC'):
    '''Extract dxf object extended data.'''
    retval= list()
    xdata= obj.get_xdata('XC')
    for tag in xdata:
        if(tag[0]==1000): # string data
            labels= tag[1].split(',')
            # remove leading and trailing spaces
            labels2= [x.strip(' ') for x in labels]
            retval.extend(labels2)
    return retval
    
    
class DXFImport(object):
    '''Import DXF entities.'''
    def __init__(self,dxfFileName,layerNamesToImport, getRelativeCoo, threshold= 0.01,importLines= True, importSurfaces= True, polylinesAsSurfaces= False, tolerance= .01):
        ''' Constructor.

           :param layerNamesToImport: list of regular expressions to be tested.
           :param getRelativeCoo: coordinate transformation to be applied to the
                                  points.
        '''
        self.dxfFileName= dxfFileName
        self.dxfFile= ezdxf.readfile(filename= self.dxfFileName)
        self.tolerance= tolerance
        self.impLines= importLines
        self.impSurfaces= importSurfaces
        self.polylinesAsSurfaces= polylinesAsSurfaces
        self.layersToImport= self.getLayersToImport(layerNamesToImport)
        if(len(self.layersToImport)):
            self.polyfaceQuads= dict()
            self.polylineQuads= dict()
            self.getRelativeCoo= getRelativeCoo
            self.threshold= threshold
            self.labelDict= {}
            self.importGroups();
            self.kPointsNames= self.selectKPoints()
            self.importPoints()
            if(self.impLines):
                self.importLines()
            else:
                self.lines= {}
            if(self.impSurfaces):
                self.importFaces()
            else:
                self.facesByLayer= {}
        else:
            self.kPoints= None

    def getIndexNearestPoint(self, pt):
        return cdist([pt], self.kPoints).argmin()

    def getNearestPoint(self, pt):
        return self.kPoints[self.getIndexNearestPoint(pt)]

    def importGroups(self):
        ''' Import the DXF groups on the file.'''
        self.groups= self.dxfFile.groups
        self.entitiesGroups= dict()
        for g in self.groups:
            groupName= g[0]
            grp= g[1]
            for h in grp.handles():
                if h in self.entitiesGroups:
                    self.entitiesGroups[h].append(groupName)
                else:
                    self.entitiesGroups[h]= [groupName]

    def getLayersToImport(self, namesToImport):
        '''Return the layers names that will be imported according to the
           regular expressions contained in the second argument.

           :param namesToImport: list of regular expressions to be tested.
        '''
        retval= []
        for layer in self.dxfFile.layers:
            layerName= layer.dxf.name
            if(layerToImport(layerName,namesToImport)):
                retval.append(layerName)
        if(len(retval)==0):
            lmsg.warning('No layers to import (names to import: '+str(namesToImport)+')')
        return retval

    def extractPoints(self):
        '''Extract the points from the entities argument.'''
        retval_pos= []
        retval_labels= []
        def append_point(pt, layerName, pointName, objLabels):
            '''Append the point to the lists.'''
            retval_pos.append(self.getRelativeCoo(pt))
            # layer name as label.
            ptLabels= [layerName]
            # xdata as label.
            for l in objLabels:
                ptLabels.append(l)
            retval_labels.append((pointName, ptLabels))
        count= 0
        for obj in self.dxfFile.entities:
            type= obj.dxftype()
            layerName= obj.dxf.layer
            objName= obj.dxf.handle
            pointName= objName
            # xdata
            objLabels= list()
            if(obj.has_xdata('XC')):
                objLabels.extend(get_extended_data(obj))
            # groups
            if(objName in self.entitiesGroups):
                objLabels.extend(self.entitiesGroups[objName])
            if(layerName in self.layersToImport):
                if(type == 'POINT'):
                    count+= 1
                    pointName+= str(count)
                    append_point(obj.dxf.location, layerName, pointName, objLabels)
                if(self.impSurfaces):
                    if(type == '3DFACE'):
                        objPoints= [obj.dxf.vtx0, obj.dxf.vtx1, obj.dxf.vtx2, obj.dxf.vtx3]
                        for pt in objPoints:
                            count+= 1
                            pointName+= str(count)
                            append_point(pt, layerName, pointName, objLabels)
                    elif(type == 'POLYLINE' and obj.get_mode()== 'AcDbPolyFaceMesh'): # POLYFACE
                        self.polyfaceQuads[objName]= decompose_polyface(obj, tol= self.tolerance)
                        for q in self.polyfaceQuads[objName]:
                            for pt in q:
                                count+= 1
                                pointName+= str(count)
                                append_point(pt, layerName, pointName, objLabels)
                if(type == 'LINE'):
                    for pt in [obj.dxf.start,obj.dxf.end]:
                        count+= 1
                        pointName+= str(count)
                        append_point(pt, layerName, pointName, objLabels)
                elif((type == 'POLYLINE') or (type == 'LWPOLYLINE')):
                    if(self.polylinesAsSurfaces):
                        self.polylineQuads[objName]= decompose_polyline(obj, tol= self.tolerance)
                        for q in self.polylineQuads[objName]:
                            for pt in q:
                                count+= 1
                                pointName+= str(count)
                                append_point(pt, layerName, pointName, objLabels)
                    else:
                        pts= obj.points
                        for pt in pts:
                            count+= 1
                            pointName+= str(count)
                            append_point(pt, layerName, pointName, objLabels)
        return retval_pos, retval_labels

    def selectKPoints(self):
        '''Selects the k-points to be used in the model. All the points that
           are closer than the threshold distance are melted into one k-point.
        '''
        points, layers= self.extractPoints()
        if(len(points)>0):
            self.kPoints= [points[0]]
            pointName= layers[0][0]
            objLabels= layers[0][1]
            self.labelDict[pointName]= objLabels
            indexDict= dict()
            indexDict[0]= pointName
            for p, l in zip(points, layers):
                pointName= l[0]
                objLabels= l[1]
                indexNearestPoint= self.getIndexNearestPoint(p)
                nearestPoint= self.kPoints[indexNearestPoint]
                dist= cdist([p],[nearestPoint])[0][0]
                if(dist>self.threshold): # new point.
                    indexNearestPoint= len(self.kPoints) # The point itself.
                    self.kPoints.append(p)
                    self.labelDict[pointName]= objLabels
                    indexDict[indexNearestPoint]= pointName
                else:
                    pointName= indexDict[indexNearestPoint]
                    labels= self.labelDict[pointName]
                    for l in objLabels:
                        if(not l in labels):
                            labels.append(l)
        else:
            lmsg.warning('No points in DXF file.')
        return indexDict

    def importPoints(self):
        ''' Import points from DXF.'''
        self.points= dict()
        for obj in self.dxfFile.entities:
            type= obj.dxftype()
            pointName= obj.dxf.handle
            layerName= obj.dxf.layer
            if(layerName in self.layersToImport):
                if(type == 'POINT'):
                    vertices= [-1]
                    p= self.getRelativeCoo(obj.dxf.location)
                    vertices[0]= self.getIndexNearestPoint(p)
                    self.points[pointName]= vertices
                    self.labelDict[pointName]= [layerName]
                    
    def getOrientation(self, p0, p1, length):
        ''' Return the points in the order that makes the resulting
            vector to point outwards the origin.'''
        idx0= self.getIndexNearestPoint(p0)
        idx1= self.getIndexNearestPoint(p1)
        v0= self.kPoints[idx0]
        v1= self.kPoints[idx1]
        deltas= [abs(v0[0]-v1[0]), abs(v0[1]-v1[1]), abs(v0[2]-v1[2])]
        indexes= sorted(range(len(deltas)), key=lambda k: deltas[k])
        i0= indexes[2]; i1= indexes[1]; i2= indexes[0]
        if(v0[i0]>v1[i0]): # r1<r2
            idx0, idx1= idx1, idx0 # swap
        elif(abs(v0[i0]-v1[i0])<length/1e4): # x1==x2
            if(v0[i1]>v1[i1]):
                idx0, idx1= idx1, idx0 # swap
            elif(abs(v0[i1]-v1[i1])<length/1e4): # y1==y2
                if(v0[i2]>v1[i2]):
                    idx0, idx1= idx1, idx0 # swap
        return idx0, idx1

    def importLines(self):
        ''' Import lines from DXF.'''
        self.lines= {}
        self.polylines= {}
        for obj in self.dxfFile.entities:
            type= obj.dxftype()
            lineName= obj.dxf.handle
            layerName= obj.dxf.layer
            if(layerName in self.layersToImport):
                if(type == 'LINE'):
                    vertices= [-1,-1]
                    p1= self.getRelativeCoo(obj.dxf.start)
                    p2= self.getRelativeCoo(obj.dxf.end)
                    length= cdist([p1],[p2])[0][0]
                    # Try to have all lines with the
                    # same orientation.
                    idx0, idx1= self.getOrientation(p1, p2, length)
                    # end orientation.
                    vertices[0]= idx0
                    vertices[1]= idx1
                    if(vertices[0]==vertices[1]):
                        lmsg.error('Error in line '+lineName+' vertices are equal: '+str(vertices))
                    if(length>self.threshold):
                        self.lines[lineName]= vertices
                        objLabels= [layerName]
                        # xdata
                        if(obj.has_xdata('XC')):
                            objLabels.extend(get_extended_data(obj))
                        # groups
                        if(lineName in self.entitiesGroups):
                            objLabels.extend(self.entitiesGroups[lineName])
                        self.labelDict[lineName]= objLabels
                    else:
                        lmsg.error('line too short: '+str(p1)+','+str(p2)+str(length))
                elif((type == 'POLYLINE') or (type == 'LWPOLYLINE')):
                    if(not self.polylinesAsSurfaces): # Import as lines
                        vertices= list()
                        for p in obj.points:
                            rCoo= self.getRelativeCoo(p)
                            vertices.append(self.getIndexNearestPoint(rCoo))
                        v1= vertices[0]
                        for v2 in vertices[1:]:
                            if(vertices[0]==vertices[1]):
                                lmsg.error('Error in line '+lineName+' vertices are equal: '+str(vertices))
                            else:
                                name= lineName+str(v1)+str(v2)
                                self.lines[name]= [v1,v2]
                                objLabels= [layerName]
                                # xdata
                                if(obj.has_xdata('XC')):
                                    objLabels.extend(get_extended_data(obj))
                                # groups
                                if(lineName in self.entitiesGroups):
                                    objLabels.extend(self.entitiesGroups[lineName])
                                self.labelDict[name]= objLabels
                            v1= v2

    def importFaces(self):
      ''' Import 3D faces from DXF.'''
      self.facesByLayer= {}
      for name in self.layersToImport:
        self.facesByLayer[name]= dict()

      for obj in self.dxfFile.entities:
        type= obj.dxftype()
        layerName= obj.dxf.layer
        if(layerName in self.layersToImport):
            facesDict= self.facesByLayer[layerName]
            if(type == '3DFACE'):
                vertices= list()
                objPoints= [obj.dxf.vtx0, obj.dxf.vtx1, obj.dxf.vtx2, obj.dxf.vtx3]
                for pt in objPoints:
                    p= self.getRelativeCoo(pt)
                    idx= self.getIndexNearestPoint(p)
                    vertices.append(idx)
                self.labelDict[obj.dxf.handle]= [layerName]
                facesDict[obj.dxf.handle]= vertices
            elif(type == 'POLYFACE'):
                count= 0
                for q in self.polyfaceQuads[obj.dxf.handle]:
                    vertices= list()
                    for pt in q:
                        p= self.getRelativeCoo(pt)
                        idx= self.getIndexNearestPoint(p)
                        if not idx in vertices:
                            vertices.append(idx)
                        else:
                            lmsg.error('Point p: '+str(p)+' idx: '+str(idx)+' repeated in '+str(q)+' vertices: '+str(vertices))
                    count+= 1
                    id= obj.dxf.handle+'_'+str(count)
                    self.labelDict[id]= [layerName]
                    facesDict[id]= vertices
            elif((type == 'POLYLINE') or (type == 'LWPOLYLINE')):
                count= 0
                if(self.polylinesAsSurfaces): # Import as surfaces
                    for q in self.polylineQuads[obj.dxf.handle]:
                        vertices= list()
                        for pt in q:
                            p= self.getRelativeCoo(pt)
                            idx= self.getIndexNearestPoint(p)
                            if not idx in vertices:
                                vertices.append(idx)
                            else:
                                lmsg.error('Point p: '+str(p)+' idx: '+str(idx)+' repeated in '+str(q)+' vertices: '+str(vertices))
                        count+= 1
                        id= obj.dxf.handle+'_'+str(count)
                        self.labelDict[id]= [layerName]
                        facesDict[id]= vertices
            elif(type == 'LINE'):
                count= 0
                # Nothing to do with lines for the moment.
            elif(type == 'POINT'):
                count= 0
                # Nothing to do with points for the moment.
            else:
              lmsg.log('Entity of type: '+type+' ignored.')      


    def exportBlockTopology(self, name):
        retval= bte.BlockData()
        retval.name= name
        retval.dxfFileName= self.dxfFileName

        counter= 0
        if(self.kPoints):
            for p in self.kPoints:
                key= self.kPointsNames[counter]
                retval.appendPoint(id= counter,x= p[0],y= p[1],z= p[2], labels= self.labelDict[key])
                counter+= 1

            counter= 0
            for key in self.lines:
                line= self.lines[key]
                block= bte.BlockRecord(counter,'line',line,self.labelDict[key])
                retval.appendBlock(block)
                counter+= 1

            for name in self.layersToImport:
                fg= self.facesByLayer[name]
                for key in fg:
                    face= fg[key]
                    block= bte.BlockRecord(counter,'face',face,self.labelDict[key])
                    retval.appendBlock(block)
                    counter+= 1
        else:
            lmsg.warning('Nothing to export.')
        return retval
    


class OldDxfReader(object):
  '''Reading of DXF entities for further processing.'''
  def __init__(self,tol= 1e-3):
    self.tol= tol
  def newKeyPoint(self,pt):
    retval= None
    pos3D= geom.Pos3d(pt[0],pt[1],pt[2])
    dist= 1e9
    nearestPoint= self.pointHandler.getNearest(pos3D)
    if(nearestPoint):
      dist= nearestPoint.getPos.distPos3d(pos3D)
    if(dist>self.tol):
      retval= self.pointHandler.newPntFromPos3d(pos3D)
    return retval
  def newLine(self,l):
    start= l.dxf.start
    posStart= geom.Pos3d(start[0],start[1],start[2])
    nearestPointStart= self.pointHandler.getNearest(posStart)
    end= l.dxf.end
    posEnd= geom.Pos3d(end[0],end[1],end[2])
    nearestPointEnd= self.pointHandler.getNearest(posEnd)
    return self.lineHandler.newLine(nearestPointStart.tag,nearestPointEnd.tag)
  def read_points(self,entities,layerName):
    retval= []
    for obj in entities:
      if(obj.dxf.layer == layerName):
        type= obj.dxftype()
        color= obj.color
        if(type=='LINE'):
          pt= self.newKeyPoint(obj.start)
          if(pt):
            retval.append(pt.tag)
          pt= self.newKeyPoint(obj.end)
          if(pt):
            retval.append(pt.tag)
        elif((type == 'POLYLINE') or (type == 'LWPOLYLINE')):
          pts= obj.points
          for p in pts:
            pt= self.newKeyPoint(p)
            if(pt):
              retval.append(pt.tag)
    return retval
  def read_lines(self,entities,layerName):
    retval= []
    for obj in entities:
      if(obj.dxf.layer == layerName):
        type= obj.dxftype()
        color= obj.color
        if(type=='LINE'):
          retval.append(self.newLine(obj).tag)
        if((type == 'POLYLINE') or (type == 'LWPOLYLINE')):
          pts= obj.points
          sz= len(pts)
          for i in range(0,sz):
            l= ezdxf.Line()
            l.start= pts[i]
            l.end= pts[i+1]
            retval.append(self.newLine(l).tag)
    return retval
  def read(self,dxf_file_name,xc_preprocessor,layers):
    self.dxf= ezdxf.readfile(dxf_file_name)
    self.preprocessor= xc_preprocessor
    self.pointHandler= self.preprocessor.getMultiBlockTopology.getPoints
    self.lineHandler= self.preprocessor.getMultiBlockTopology.getLines
    self.pointsInLayer= {}
    self.blocksInLayer= {}
    for l in layers:
      self.pointsInLayer[l]= self.read_points(self.dxf.entities,l)
      self.blocksInLayer[l]= self.read_lines(self.dxf.entities,l)


