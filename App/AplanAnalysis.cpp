/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2013 Jürgen Riegel <FreeCAD@juergen-riegel.net>         *
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

#include <App/Application.h>
#include <App/Document.h>
#include <App/DocumentObject.h>
#include <App/DocumentObjectPy.h>
#include <App/DocumentObjectGroup.h>
#include <App/FeaturePython.h>
#include <App/FeaturePythonPyImp.h>
#include <Base/BaseClass.h>
#include <Base/Placement.h>
#include <Base/Uuid.h>
#include <Base/Tools.h>

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include <Mod/Aplan/App/AplanAnalysisPy.h>
#include <Mod/Aplan/App/AplanCompoundGroup.hpp>
#include <Mod/Aplan/App/AplanConnectionDetector.hpp>
#include <Mod/Aplan/App/AplanPartFilter.hpp>

using namespace Aplan;
using namespace App;

PROPERTY_SOURCE(Aplan::AplanAnalysis, App::DocumentObjectGroup)

AplanAnalysis::AplanAnalysis()
{
    Base::Uuid id;
    ADD_PROPERTY_TYPE(Uid, (id), 0, App::Prop_None, "UUID of the Analysis");
    ADD_PROPERTY_TYPE(WorkingDir, (0), "Aplan", (App::PropertyType)(App::Prop_None), "Working directory of the Analysis");
}

AplanAnalysis::~AplanAnalysis()
{
}

PyObject *AplanAnalysis::getPyObject()
{
    if (PythonObject.is(Py::_None()))
    {
        // ref counter is set to 1
        PythonObject = Py::Object(new AplanAnalysisPy(this), true);
    }
    return Py::new_reference_to(PythonObject);
}

std::vector<Aplan::AplanCompoundGroup *> AplanAnalysis::getCompoundGroupObjects(void) const
{
    std::vector<Aplan::AplanCompoundGroup *> objects{};
    for (const auto &obj : this->getAllChildren())
    {
        if (obj->isDerivedFrom(Aplan::AplanCompoundGroup::getClassTypeId()))
        {
            objects.push_back(static_cast<Aplan::AplanCompoundGroup *>(obj));
        }
    }
    return objects;
}

std::vector<Aplan::ConnectionDetector *> AplanAnalysis::getConnectionDetectorObjects(void) const
{
    std::vector<Aplan::ConnectionDetector *> objects{};
    for (const auto &obj : this->getAllChildren())
    {
        if (obj->isDerivedFrom(Aplan::ConnectionDetector::getClassTypeId()))
        {
            objects.push_back(static_cast<Aplan::ConnectionDetector *>(obj));
        }
    }
    return objects;
}

std::vector<Aplan::PartFilter *> AplanAnalysis::getPartFilterObjects(void) const
{
    std::vector<Aplan::PartFilter *> objects{};
    for (const auto &obj : this->getAllChildren())
    {
        if (obj->isDerivedFrom(Aplan::PartFilter::getClassTypeId()))
        {
            objects.push_back(static_cast<Aplan::PartFilter *>(obj));
        }
    }
    return objects;
}

std::string AplanAnalysis::getUniqueObjectLabel(const std::string &label, const std::vector<std::string> &extraLabels) const
{
    std::vector<std::string> objectLabels{extraLabels};
    App::Document *doc = App::GetApplication().getActiveDocument();
    const std::vector<App::DocumentObject *> objects = doc->getObjects();
    std::transform(objects.begin(), objects.end(), std::back_inserter(objectLabels),
                   [](App::DocumentObject *obj) -> std::string
                   {
                       return obj->Label.getValue();
                   });
    return Base::Tools::getUniqueName(label, objectLabels, 3);
}

// Dummy class 'DocumentObject' in Aplan namespace
PROPERTY_SOURCE_ABSTRACT(Aplan::DocumentObject, App::DocumentObject)

// Python feature ---------------------------------------------------------

namespace App
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(Aplan::AplanAnalysisPython, Aplan::AplanAnalysis)
    template <>
    const char *Aplan::AplanAnalysisPython::getViewProviderName(void) const
    {
        return "AplanGui::ViewProviderAplanAnalysisPython";
    }
    /// @endcond

    // explicit template instantiation
    template class AplanAppExport FeaturePythonT<Aplan::AplanAnalysis>;
}

// ---------------------------------------------------------

namespace App
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(Aplan::FeaturePython, Aplan::DocumentObject)
    template <>
    const char *Aplan::FeaturePython::getViewProviderName(void) const
    {
        return "Gui::ViewProviderPythonFeature";
    }
    template <>
    PyObject *Aplan::FeaturePython::getPyObject(void)
    {
        if (PythonObject.is(Py::_None()))
        {
            // ref counter is set to 1
            PythonObject = Py::Object(new App::FeaturePythonPyT<App::DocumentObjectPy>(this), true);
        }
        return Py::new_reference_to(PythonObject);
    }
    // explicit template instantiation
    template class AplanAppExport FeaturePythonT<Aplan::DocumentObject>;
    /// @endcond
}
