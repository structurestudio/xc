//----------------------------------------------------------------------------
//  XC program; finite element analysis code
//  for structural analysis and design.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  This program derives from OpenSees <http://opensees.berkeley.edu>
//  developed by the  «Pacific earthquake engineering research center».
//
//  Except for the restrictions that may arise from the copyright
//  of the original program (see copyright_opensees.txt)
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
//MapFields.cc

#include "MapFields.h"
#include "preprocessor/Preprocessor.h"


#include "domain/mesh/element/Element.h"
#include "domain/mesh/node/Node.h"


//! @brief Returns true if the set exists.
bool XC::MapFields::exists(const std::string &nmb) const
  {
    const_iterator i= buscaField(nmb);
    return (i!=end());
  }

//! @brief Returns a pointer to the set which name is being passed as parameter.
XC::MapFields::iterator XC::MapFields::buscaField(const std::string &nmb)
  {
    iterator i=begin();
    for(;i!=end();i++)
      if(i->getName()==nmb) break;
    return i;
  }

//! @brief Returns a pointer to the set which name is being passed as parameter.
XC::MapFields::const_iterator XC::MapFields::buscaField(const std::string &nmb) const
  {
    const_iterator i=begin();
    for(;i!=end();i++)
      if(i->getName()==nmb) break;
    return i;
  }

//! @brief Default constructor.
XC::MapFields::MapFields(Preprocessor *prep)
  : PreprocessorContainer(prep), MovableObject(0) {}

//! @bred Defines a new field
XC::FieldInfo &XC::MapFields::newField(const std::string &field_name)
  {
    FieldInfo fi(field_name);
    fi.set_owner(this);
    push_back(fi);
    return back();
  }

//! @brief Clears all.
void XC::MapFields::clearAll(void)
  { clear(); }

//! @brief Send members through the communicator argument.
int XC::MapFields::sendData(Communicator &comm)
  {
    std::cerr << getClassName() << ":: " << __FUNCTION__
              << " not implemented." << std::endl;
    return 0;
  }

//! @brief Receives members through the communicator argument.
int XC::MapFields::recvData(const Communicator &comm)
  {
    std::cerr << getClassName() << ":: " << __FUNCTION__
              << " not implemented." << std::endl;
    return 0;
  }

//! @brief Sends object through the communicator argument.
int XC::MapFields::sendSelf(Communicator &comm)
  {
    setDbTag(comm);
    const int dataTag= getDbTag();
    inicComm(6);
    int res= sendData(comm);

    res+= comm.sendIdData(getDbTagData(),dataTag);
    if(res < 0)
      std::cerr <<  getClassName() << ":: " << __FUNCTION__
		<< "; failed to send data\n";
    return res;
  }

//! @brief Receives object through the communicator argument.
int XC::MapFields::recvSelf(const Communicator &comm)
  {
    inicComm(6);
    const int dataTag= getDbTag();
    int res= comm.receiveIdData(getDbTagData(),dataTag);

    if(res<0)
      std::cerr <<  getClassName() << ":: " << __FUNCTION__
		<< "; failed to receive ids.\n";
    else
      {
        //setTag(getDbTagDataPos(0));
        res+= recvData(comm);
        if(res<0)
          std::cerr <<  getClassName() << ":: " << __FUNCTION__
		    << "; failed to receive data.\n";
      }
    return res;
  }

