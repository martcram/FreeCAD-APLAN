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
#include <Base/Interpreter.h>
#include <Base/PyObjectBase.h>
#include <Gui/Application.h>
#include <Gui/Language/Translator.h>

#include <Mod/Aplan/Gui/ViewProviderAnalysis.hpp>
#include <Mod/Aplan/Gui/ViewProviderCompound.hpp>
#include <Mod/Aplan/Gui/ViewProviderCompoundGroup.hpp>
#include <Mod/Aplan/Gui/ViewProviderConnectionDetector.hpp>
#include <Mod/Aplan/Gui/ViewProviderConstraintGroup.hpp>
#include <Mod/Aplan/Gui/ViewProviderGeomConstraints.hpp>
#include <Mod/Aplan/Gui/ViewProviderObstructionDetector.hpp>
#include <Mod/Aplan/Gui/ViewProviderPartFilter.hpp>
#include <Mod/Aplan/Gui/ViewProviderTopoConstraints.hpp>
#include <Mod/Aplan/Gui/Workbench.hpp>

void CreateAplanCommands(void);

void loadAplanResource()
{
    // add resources and reloads the translators
    Q_INIT_RESOURCE(Aplan);
    Gui::Translator::instance()->refresh();
}

namespace AplanGui
{
    extern PyObject *initModule();
}

/* Python entry */
PyMOD_INIT_FUNC(AplanGui)
{
    if (!Gui::Application::Instance)
    {
        PyErr_SetString(PyExc_ImportError, "Cannot load Gui module in console application.");
        PyMOD_Return(0);
    }

    // load dependent modules
    try {
        Base::Interpreter().loadModule("PartGui");
    }
    catch(const Base::Exception& e) {
        PyErr_SetString(PyExc_ImportError, e.what());
        PyMOD_Return(0);
    }

    PyObject *mod = AplanGui::initModule();
    Base::Console().Log("Loading GUI of APLAN module... done\n");

    // instantiating the commands
    CreateAplanCommands();

    // addition objects
    AplanGui::Workbench::init();

    AplanGui::ViewProviderAplanAnalysis::init();
    AplanGui::ViewProviderAplanAnalysisPython::init();

    AplanGui::ViewProviderCompound::init();
    AplanGui::ViewProviderCompoundPython::init();

    AplanGui::ViewProviderCompoundGroup::init();
    AplanGui::ViewProviderCompoundGroupPython::init();

    AplanGui::ViewProviderConnectionDetector::init();
    AplanGui::ViewProviderConnectionDetectorPython::init();

    AplanGui::ViewProviderConstraintGroup::init();
    AplanGui::ViewProviderConstraintGroupPython::init();

    AplanGui::ViewProviderGeomConstraints::init();
    AplanGui::ViewProviderGeomConstraintsPython::init();

    AplanGui::ViewProviderObstructionDetector::init();
    AplanGui::ViewProviderObstructionDetectorPython::init();

    AplanGui::ViewProviderPartFilter::init();
    AplanGui::ViewProviderPartFilterPython::init();

    AplanGui::ViewProviderTopoConstraints::init();
    AplanGui::ViewProviderTopoConstraintsPython::init();

    // add resources and reloads the translators
    loadAplanResource();

    PyMOD_Return(mod);
}
