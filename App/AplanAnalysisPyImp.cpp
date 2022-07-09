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

#include <Mod/Aplan/App/AplanAnalysis.hpp>
#include <Mod/Aplan/App/AplanCompoundGroup.hpp>
#include <Mod/Aplan/App/AplanConnectionDetector.hpp>
#include <Mod/Aplan/App/AplanConstraintGroup.hpp>
#include <Mod/Aplan/App/AplanObstructionDetector.hpp>
#include <Mod/Aplan/App/AplanPartFilter.hpp>

// inclusion of the generated files (generated out of AplanAnalysisPy.xml)
#include <Mod/Aplan/App/AplanAnalysisPy.h>
#include <Mod/Aplan/App/AplanAnalysisPy.cpp>

using namespace Aplan;

// returns a string which represents the object e.g. when printed in python
std::string AplanAnalysisPy::representation(void) const
{
    return std::string("<AplanAnalysis object>");
}

// ===== Methods ============================================================

Py::List AplanAnalysisPy::getComponents(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<App::DocumentObject *> objects = getAplanAnalysisPtr()->getComponents();
        for (App::DocumentObject *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjects;
}

Py::List AplanAnalysisPy::getCompoundGroupObjects(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<Aplan::AplanCompoundGroup *> objects = getAplanAnalysisPtr()->getCompoundGroupObjects();
        for (Aplan::AplanCompoundGroup *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjects;
}

Py::List AplanAnalysisPy::getConnectionDetectorObjects(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<Aplan::ConnectionDetector *> objects = getAplanAnalysisPtr()->getConnectionDetectorObjects();
        for (Aplan::ConnectionDetector *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjects;
}

Py::List AplanAnalysisPy::getConstraintGroupObjects(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<Aplan::AplanConstraintGroup *> objects = getAplanAnalysisPtr()->getConstraintGroupObjects();
        for (Aplan::AplanConstraintGroup *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjects;
}

Py::List AplanAnalysisPy::getObstructionDetectorObjects(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<Aplan::ObstructionDetector *> objects = getAplanAnalysisPtr()->getObstructionDetectorObjects();
        for (Aplan::ObstructionDetector *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjects;
}

Py::List AplanAnalysisPy::getPartFilterObjects(void) const
{
    Py::List pyObjects;
    try
    {
        std::vector<Aplan::PartFilter *> objects = getAplanAnalysisPtr()->getPartFilterObjects();
        for (Aplan::PartFilter *o : objects)
        {
            pyObjects.append(Py::Object(o->getPyObject()));
        }
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjects;
}

PyObject *AplanAnalysisPy::getUniqueObjectLabel(PyObject *args)
{
    const char *label{};
    PyObject *pList{NULL};
    if (!PyArg_ParseTuple(args, "s|O!", &label, &PyList_Type, &pList)) // "|" indicates that the remaining arguments in the Python argument list are optional.
    {
        PyErr_SetString(PyExc_TypeError, "getUniqueObjectLabel: 1st parameter must be a string, 2nd parameter must be a list.");
        return 0;
    }

    std::vector<std::string> extraLabels{};
    if (pList != NULL)
    {
        Py_ssize_t n{PyList_Size(pList)};
        for (Py_ssize_t i = 0; i < n; i++)
        {
            PyObject *pItem = PyList_GetItem(pList, i);
            if (PyUnicode_Check(pItem))
            {
                extraLabels.push_back(std::string(PyBytes_AsString(PyUnicode_AsUTF8String(pItem))));
            }
            else
            {
                PyErr_SetString(PyExc_TypeError, "getUniqueObjectLabel: List items must be strings.");
                return 0;
            }
        }
    }

    PyObject *pyObjectName{};
    try
    {
        std::string uniqueLabel = getAplanAnalysisPtr()->getUniqueObjectLabel(label, extraLabels);
        pyObjectName = PyUnicode_FromString(uniqueLabel.c_str());
    }
    catch (const std::exception &e)
    {
        PyErr_SetString(Base::PyExc_FC_GeneralError, e.what());
    }
    return pyObjectName;
}

// ===== custom attributes ============================================================

PyObject *AplanAnalysisPy::getCustomAttributes(const char * /*attr*/) const
{
    return 0;
}

int AplanAnalysisPy::setCustomAttributes(const char * /*attr*/, PyObject * /*obj*/)
{
    return 0;
}
