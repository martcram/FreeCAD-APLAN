/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2008 Werner Mayer <werner.wm.mayer@gmx.de>              *
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

#include <CXX/Extensions.hxx>
#include <CXX/Objects.hxx>

#include <App/DocumentObjectPy.h>
#include <Gui/Application.h>
#include <Gui/Document.h>

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include "ActiveAnalysisObserver.hpp"

namespace AplanGui
{
    class Module : public Py::ExtensionModule<Module>
    {
    public:
        Module() : Py::ExtensionModule<Module>("AplanGui")
        {
            add_varargs_method("setActiveAnalysis", &Module::setActiveAnalysis,
                               "setActiveAnalysis(AnalysisObject) -- Set the Analysis object in work.");
            add_noargs_method("unsetActiveAnalysis", &Module::unsetActiveAnalysis,
                              "unsetActiveAnalysis() -- Unset the Analysis object in work.");
            add_varargs_method("getActiveAnalysis", &Module::getActiveAnalysis,
                               "getActiveAnalysis() -- Returns the Analysis object in work.");
            initialize("This module is the AplanGui module."); // register with Python
        }

        virtual ~Module() {}

    private:
        virtual Py::Object invoke_method_varargs(void *method_def, const Py::Tuple &args)
        {
            try
            {
                return Py::ExtensionModule<Module>::invoke_method_varargs(method_def, args);
            }
            catch (const Base::Exception &e)
            {
                throw Py::RuntimeError(e.what());
            }
            catch (const std::exception &e)
            {
                throw Py::RuntimeError(e.what());
            }
        }
        Py::Object setActiveAnalysis(const Py::Tuple &args)
        {
            if (AplanGui::ActiveAnalysisObserver::instance()->hasActiveObject())
            {
                AplanGui::ActiveAnalysisObserver::instance()->highlightActiveObject(Gui::HighlightMode::UserDefined, false);
                AplanGui::ActiveAnalysisObserver::instance()->setActiveObject(0);
            }

            PyObject *object = 0;
            if (PyArg_ParseTuple(args.ptr(), "|O!", &(App::DocumentObjectPy::Type), &object) && object)
            {
                App::DocumentObject *obj = static_cast<App::DocumentObjectPy *>(object)->getDocumentObjectPtr();
                if (!obj || !obj->getTypeId().isDerivedFrom(Aplan::AplanAnalysis::getClassTypeId()))
                {
                    throw Py::Exception(Base::BaseExceptionFreeCADError, "Active Analysis object have to be of type Aplan::AplanAnalysis!");
                }

                // get the gui document of the Analysis Item
                AplanGui::ActiveAnalysisObserver::instance()->setActiveObject(static_cast<Aplan::AplanAnalysis *>(obj));
                AplanGui::ActiveAnalysisObserver::instance()->highlightActiveObject(Gui::HighlightMode::UserDefined, true);
            }

            return Py::None();
        }
        Py::Object unsetActiveAnalysis()
        {
            AplanGui::ActiveAnalysisObserver::instance()->unsetActiveObject();
            return Py::None();
        }
        Py::Object getActiveAnalysis(const Py::Tuple &args)
        {
            if (!PyArg_ParseTuple(args.ptr(), ""))
                throw Py::Exception();
            if (AplanGui::ActiveAnalysisObserver::instance()->hasActiveObject())
            {
                return Py::asObject(AplanGui::ActiveAnalysisObserver::instance()->getActiveObject()->getPyObject());
            }
            return Py::None();
        }
    };

    PyObject *initModule()
    {
        return (new Module)->module().ptr();
    }
} // namespace AplanGui
