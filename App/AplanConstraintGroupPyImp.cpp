/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2009 Jürgen Riegel <juergen.riegel@web.de>              *
 *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
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

#include <Base/PyObjectBase.h>
#include <exception>

#include <Mod/Aplan/App/AplanConstraintGroup.hpp>
#include <Mod/Aplan/App/AplanTopoConstraints.hpp>

// inclusion of the generated files (generated out of AplanConstraintGroupPy.xml)
#include <Mod/Aplan/App/AplanConstraintGroupPy.h>
#include <Mod/Aplan/App/AplanConstraintGroupPy.cpp>

using namespace Aplan;

// returns a string which represents the object e.g. when printed in python
std::string AplanConstraintGroupPy::representation(void) const
{
    return std::string("<ConstraintGroup object>");
}

// ===== Methods ============================================================

Py::List AplanConstraintGroupPy::getTopoConstraintsObjects(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<Aplan::TopoConstraints *> objects = getAplanConstraintGroupPtr()->getTopoConstraintsObjects();
        for (Aplan::TopoConstraints *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::BaseExceptionFreeCADError, e.what());
    }
    return pyObjects;
}

// ===== custom attributes ============================================================

PyObject *AplanConstraintGroupPy::getCustomAttributes(const char * /*attr*/) const
{
    return 0;
}

int AplanConstraintGroupPy::setCustomAttributes(const char * /*attr*/, PyObject * /*obj*/)
{
    return 0;
}
