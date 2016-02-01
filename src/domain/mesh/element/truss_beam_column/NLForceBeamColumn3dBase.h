//----------------------------------------------------------------------------
//  programa XC; cálculo mediante el método de los elementos finitos orientado
//  a la solución de problemas estructurales.
//
//  Copyright (C)  Luis Claudio Pérez Tato
//
//  El programa deriva del denominado OpenSees <http://opensees.berkeley.edu>
//  desarrollado por el «Pacific earthquake engineering research center».
//
//  Salvo las restricciones que puedan derivarse del copyright del
//  programa original (ver archivo copyright_opensees.txt) este
//  software es libre: usted puede redistribuirlo y/o modificarlo 
//  bajo los términos de la Licencia Pública General GNU publicada 
//  por la Fundación para el Software Libre, ya sea la versión 3 
//  de la Licencia, o (a su elección) cualquier versión posterior.
//
//  Este software se distribuye con la esperanza de que sea útil, pero 
//  SIN GARANTÍA ALGUNA; ni siquiera la garantía implícita
//  MERCANTIL o de APTITUD PARA UN PROPÓSITO DETERMINADO. 
//  Consulte los detalles de la Licencia Pública General GNU para obtener 
//  una información más detallada. 
//
// Debería haber recibido una copia de la Licencia Pública General GNU 
// junto a este programa. 
// En caso contrario, consulte <http://www.gnu.org/licenses/>.
//----------------------------------------------------------------------------
//NLForceBeamColumn3dBase.h

#ifndef NLForceBeamColumn3dBase_h
#define NLForceBeamColumn3dBase_h

#include <domain/mesh/element/truss_beam_column/BeamColumnWithSectionFDTrf3d.h>
#include <utility/matrix/Matrix.h>
#include <utility/matrix/Vector.h>
#include "domain/mesh/element/fvectors/FVectorBeamColumn3d.h"
#include "domain/mesh/element/truss_beam_column/EsfBeamColumn3d.h"
#include "domain/mesh/element/coordTransformation/CrdTransf3d.h"

namespace XC {

//! \ingroup ElemBarra
//
//! @brief Elemento barra no lineal con material de tipo SeccionBarraPrismatica para problemas tridimensionales.
class NLForceBeamColumn3dBase: public BeamColumnWithSectionFDTrf3d
  {
    NLForceBeamColumn3dBase &operator=(const NLForceBeamColumn3dBase &);
  protected:
    static const size_t NDM; //!< dimension of the problem (3d)
    static const int NND; //!< number of nodal dof's
    static const size_t NEGD; //!< number of element global dof's
    static const size_t NEBD; //!< number of element dof's in the basic system
    static const double DefaultLoverGJ;

    
    // internal data
    double rho; //!<mass density per unit length
    int maxIters; //!<maximum number of local iterations
    double tol;	 //!<tolerance for relative energy norm for local iterations

    int initialFlag; //!<indicates if the element has been initialized
    bool isTorsion;
	
    Matrix kv; //!<stiffness matrix in the basic system 
    EsfBeamColumn3d Se; //!<element resisting forces in the basic system

    Matrix kvcommit; //!<commited stiffness matrix in the basic system
    EsfBeamColumn3d Secommit; //!<commited element end forces in the basic system

    std::vector<Matrix> fs; //!<array of section flexibility matrices
    std::vector<Vector> vs; //!<array of section deformation vectors
    std::vector<Vector> Ssr; //!<array of section resisting force vectors
    std::vector<Vector> vscommit; //!<array of commited section deformation vectors

    Matrix sp; //!<Applied section forces due to element loads, 5 x nSections
    FVectorBeamColumn3d p0; //!<Reactions in the basic system due to element loads

    mutable Matrix Ki;

    static Matrix theMatrix;
    static Vector theVector;
    static double workArea[];

    void resizeMatrices(const size_t &nSections);
    void initializeSectionHistoryVariables(void);

    int sendData(CommParameters &cp);
    int recvData(const CommParameters &cp);

  public:
    NLForceBeamColumn3dBase(int tag,int classTag,int numSec= 0);
    NLForceBeamColumn3dBase(int tag,int classTag,int numSec,const Material *theSection,const CrdTransf *coordTransf);
    NLForceBeamColumn3dBase(const NLForceBeamColumn3dBase &otro);

    void setSection(const SeccionBarraPrismatica *sccModel);

    int getNumDOF(void) const;

    double getRho(void) const
      { return rho; }
    void setRho(const double &r)
      { rho= r; }

    const Matrix &getTangentStiff(void) const;

    const Vector &getResistingForce(void) const;

    inline double getAN1(void) //Axial force which acts over the element in his back end.
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.AN1()+p0[0];
      }
    inline double getAN2(void) //Axial force which acts over the element in his front end.
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.AN2();
      }
    inline double getN1(void) //Axial force in the front end.
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.AN1()-p0[0];
      }
    inline double getN2(void) //Axial force in the back end.
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.AN2();
      }
    inline double getN(void) //Mean axial force.
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return (-Secommit.AN1()-p0[0]+Secommit.AN2())/2.0;
      }
    inline double getAMz1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Mz1(); //Momento z que se ejerce sobre la barra en su extremo dorsal.
      }
    inline double getAMz2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Mz2(); //Momento z que se ejerce sobre la barra en su extremo frontal.
      }
    inline double getMz1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.Mz1(); //Momento z en su extremo dorsal.
      }
    inline double getMz2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.Mz2(); //Momento z en su extremo frontal.
      }
    inline double getVy(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Vy(theCoordTransf->getInitialLength()); //Cortante y.
      }
    inline double getAVy1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Vy(theCoordTransf->getInitialLength())+p0[1]; //Cortante y que se ejerce sobre la barra en su extremo dorsal.
      }
    inline double getAVy2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.Vy(theCoordTransf->getInitialLength())+p0[2]; //Cortante y que se ejerce sobre la barra en su extremo frontal.
      }
    inline double getVy1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.Vy(theCoordTransf->getInitialLength())-p0[1]; //Cortante y en su extremo dorsal.
      }
    inline double getVy2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Vy(theCoordTransf->getInitialLength())-p0[2]; //Cortante y en su extremo frontal.
      }
    inline double getVz(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Vz(theCoordTransf->getInitialLength()); //Cortante z.
      }
    inline double getAVz1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Vz(theCoordTransf->getInitialLength())+p0[3]; //Cortante z que se ejerce sobre la barra en su extremo dorsal.
      }
    inline double getAVz2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.Vz(theCoordTransf->getInitialLength())+p0[4]; //Cortante z que se ejerce sobre la barra en su extremo frontal.
      }
    inline double getVz1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return -Secommit.Vz(theCoordTransf->getInitialLength())-p0[3]; //Cortante z en su extremo dorsal.
      }
    inline double getVz2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.Vz(theCoordTransf->getInitialLength())-p0[4]; //Cortante z en su extremo frontal.
      }
    inline double getMy1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.My1(); //Momento y en el extremo dorsal.
      }
    inline double getMy2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.My2(); //Momento y en el extremo frontal.
      }
    inline double getT(void) //Element's torque.
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.T();
      }
    inline double getT1(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.T1(); //+p0[0]; //Torsor en el extremo dorsal.
      }
    inline double getT2(void)
      {                 //¡Warning! call "calc_resisting_force" before calling this method.
        return Secommit.T2(); //Torsor en el extremo frontal.
      }

  };
} // end of XC namespace

#endif

