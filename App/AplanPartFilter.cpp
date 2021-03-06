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

#include <App/DocumentObject.h>
#include <App/DocumentObjectPy.h>
#include <App/FeaturePython.h>
#include <App/FeaturePythonPyImp.h>

#include <Mod/Aplan/App/AplanPartFilter.hpp>

using namespace Aplan;

PROPERTY_SOURCE(Aplan::PartFilter, App::DocumentObject)

PartFilter::PartFilter()
{
    ADD_PROPERTY_TYPE(ExcludedParts, (0), "PartFilter", (App::PropertyType)(App::Prop_None),
                      "References to the parts that were excluded from analysis");
    ADD_PROPERTY_TYPE(Compounds, (0), "PartFilter", (App::PropertyType)(App::Prop_None),
                      "References to the compounds of components");
}

PartFilter::~PartFilter()
{
}

// Python feature ---------------------------------------------------------

namespace App
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(Aplan::PartFilterPython, Aplan::PartFilter)
    template <>
    const char *Aplan::PartFilterPython::getViewProviderName(void) const
    {
        return "AplanGui::ViewProviderPartFilterPython";
    }

    template <>
    PyObject *Aplan::PartFilterPython::getPyObject(void)
    {
        if (PythonObject.is(Py::_None()))
        {
            // ref counter is set to 1
            PythonObject = Py::Object(new App::FeaturePythonPyT<App::DocumentObjectPy>(this), true);
        }
        return Py::new_reference_to(PythonObject);
    }

    // explicit template instantiation
    template class AplanAppExport FeaturePythonT<Aplan::PartFilter>;

    /// @endcond
}
