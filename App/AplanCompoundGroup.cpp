/******************************************************************************
 *                                                                            *
 *   Copyright (c) 2013 Jan Rheinländer <jrheinlaender@users.sourceforge.net> *
 *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>           *
 *                                                                            *
 *   This file is part of the FreeCAD CAx development system.                 *
 *                                                                            *
 *   This library is free software; you can redistribute it and/or            *
 *   modify it under the terms of the GNU Library General Public              *
 *   License as published by the Free Software Foundation; either             *
 *   version 2 of the License, or (at your option) any later version.         *
 *                                                                            *
 *   This library  is distributed in the hope that it will be useful,         *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of           *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            *
 *   GNU Library General Public License for more details.                     *
 *                                                                            *
 *   You should have received a copy of the GNU Library General Public        *
 *   License along with this library; see the file COPYING.LIB. If not,       *
 *   write to the Free Software Foundation, Inc., 59 Temple Place,            *
 *   Suite 330, Boston, MA  02111-1307, USA                                   *
 *                                                                            *
 ******************************************************************************/

#include "PreCompiled.hpp"

#include <App/DocumentObjectGroup.h>
#include <App/DocumentObjectGroupPy.h>
#include <App/FeaturePythonPyImp.h>
#include <Mod/Aplan/App/AplanCompound.hpp>
#include <Mod/Aplan/App/AplanCompoundGroup.hpp>
#include <Mod/Aplan/App/AplanCompoundGroupPy.h>

using namespace Aplan;

PROPERTY_SOURCE(Aplan::AplanCompoundGroup, App::DocumentObjectGroup)

AplanCompoundGroup::AplanCompoundGroup()
{
}

AplanCompoundGroup::~AplanCompoundGroup()
{
}

std::vector<Aplan::Compound *> AplanCompoundGroup::getCompoundObjects(void) const
{
    std::vector<Aplan::Compound *> objects{};
    for (const auto &obj : this->getAllChildren())
    {
        if (obj->isDerivedFrom(Aplan::Compound::getClassTypeId()))
        {
            objects.push_back(static_cast<Aplan::Compound *>(obj));
        }
    }
    return objects;
}

PyObject *AplanCompoundGroup::getPyObject()
{
    if (PythonObject.is(Py::_None()))
    {
        // ref counter is set to 1
        PythonObject = Py::Object(new AplanCompoundGroupPy(this), true);
    }
    return Py::new_reference_to(PythonObject);
}

// Python feature ---------------------------------------------------------

namespace App
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(Aplan::AplanCompoundGroupPython, Aplan::AplanCompoundGroup)
    template <>
    const char *Aplan::AplanCompoundGroupPython::getViewProviderName(void) const
    {
        return "AplanGui::ViewProviderAplanCompoundGroupPython";
    }

    template <>
    PyObject *Aplan::AplanCompoundGroupPython::getPyObject(void)
    {
        if (PythonObject.is(Py::_None()))
        {
            // ref counter is set to 1
            PythonObject = Py::Object(new App::FeaturePythonPyT<App::DocumentObjectGroupPy>(this), true);
        }
        return Py::new_reference_to(PythonObject);
    }

    // explicit template instantiation
    template class AplanAppExport FeaturePythonT<Aplan::AplanCompoundGroup>;

    /// @endcond
}
