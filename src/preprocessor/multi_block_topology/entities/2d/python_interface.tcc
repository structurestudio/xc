//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  XC is free software: you can redistribute it and/or modify 
//  it under the terms of the GNU General Public License as published by
//  the Free Software Foundation, either version 3 of the License, or 
//  (at your option) any later version.
//
//  This software is distributed in the hope that it will be useful, but 
//  WITHOUT ANY WARRANTY; without even the implied warranty of 
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details. 
//
//
// You should have received a copy of the GNU General Public License 
// along with this program.
// If not, see <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
//python_interface.tcc


class_<XC::Face, XC::Face *,bases<XC::CmbEdge>, boost::noncopyable >("Face", no_init)
  .add_property("nDivI", &XC::Face::NDivI, &XC::Face::setNDivI)
  .add_property("nDivJ", &XC::Face::NDivJ, &XC::Face::setNDivJ)
  .def("getContour",&XC::Face::getContour,"Return the face contour as a 3D polyline.")
   ;

class_<XC::QuadSurface, XC::QuadSurface *, bases<XC::Face>, boost::noncopyable >("QuadSurface", no_init)
  .def("defGridPoints",&XC::QuadSurface::defGridPoints)
  .def("setElemSizeI",&XC::QuadSurface::SetElemSizeI)
  .def("setElemSizeJ",&XC::QuadSurface::SetElemSizeJ)
  .def("setElemSizeIJ",&XC::QuadSurface::SetElemSizeIJ)
  .add_property("getIVector", &XC::QuadSurface::getIVector,"Return the local x vector.")
  .add_property("getJVector", &XC::QuadSurface::getJVector,"Return the local x vector.")
  .add_property("getKVector", &XC::QuadSurface::getKVector,"Return the local x vector.")
  .def("getLocalAxes",&XC::QuadSurface::getLocalAxes,"Return the surface local axes as matrix rows: [[x1,y1,z1],[x2,y2,z2],...·] .")
  .def("getPolygon",&XC::QuadSurface::getPolygon,"Return the contour as a 3D polygon.")
   ;



