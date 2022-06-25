/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2008 Jürgen Riegel <juergen.riegel@web.de>              *
 *   Copyright (c) 2021 Martijn Cramer <martijn.cramer@outlook.com>        *
 *                                                                         *
 *   This file is part of the FreeCAD CAx development system.              *
 *                                                                         *
 *   This library is free software; you can redistribute it and/or         *
 *   modify it under the terms of the GNU Library General Public           *
 *   License as published by the Free Software Foundation; either          *
 *   version 2 of the License, or (at your option) any later version.      *
 *                                                                         *
 *   This library  is distributed in the hope that it will be useful,      *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU Library General Public License for more details.                  *
 *                                                                         *
 *   You should have received a copy of the GNU Library General Public     *
 *   License along with this library; see the file COPYING.LIB. If not,    *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,         *
 *   Suite 330, Boston, MA  02111-1307, USA                                *
 *                                                                         *
 ***************************************************************************/

#include "PreCompiled.hpp"
#ifndef _PreComp_
#include <Python.h>
#endif

#include <Base/Console.h>
#include <Base/PyObjectBase.h>
#include <CXX/Extensions.hxx>
#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include <Mod/Aplan/App/AplanPartFilter.hpp>
#include <Mod/Aplan/App/AplanCompound.hpp>
#include <Mod/Aplan/App/AplanCompoundGroup.hpp>
#include <Mod/Aplan/App/AplanConnectionDetector.hpp>
#include <Mod/Aplan/App/AplanConstraintGroup.hpp>
#include <Mod/Aplan/App/AplanTopoConstraints.hpp>

namespace Aplan
{
    extern PyObject *initModule();
}

/* Python entry */
PyMOD_INIT_FUNC(Aplan)
{
    // load dependent modules
    try {
        Base::Interpreter().loadModule("Part");
    }
    catch(const Base::Exception& e) {
        PyErr_SetString(PyExc_ImportError, e.what());
        PyMOD_Return(0);
    }

    PyObject *mod = Aplan::initModule();
    Base::Console().Log("Loading the APLAN module... done\n");

    Aplan::DocumentObject::init();
    Aplan::FeaturePython::init();

    Aplan::AplanAnalysis::init();
    Aplan::AplanAnalysisPython::init();

    Aplan::Compound::init();
    Aplan::CompoundPython::init();

    Aplan::AplanCompoundGroup::init();
    Aplan::AplanCompoundGroupPython::init();

    Aplan::ConnectionDetector::init();
    Aplan::ConnectionDetectorPython::init();

    Aplan::PartFilter::init();
    Aplan::PartFilterPython::init();

    Aplan::AplanConstraintGroup::init();
    Aplan::AplanConstraintGroupPython::init();
    
    Aplan::TopoConstraints::init();
    Aplan::TopoConstraintsPython::init();

    PyMOD_Return(mod);
}