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

#ifndef APLAN_APLANANALYSIS_HPP
#define APLAN_APLANANALYSIS_HPP

#include "PreCompiled.hpp"

#include <App/DocumentObject.h>
#include <App/DocumentObjectGroup.h>
#include <App/FeaturePython.h>
#include <App/PropertyStandard.h>

#include <Mod/Aplan/App/AplanCompoundGroup.hpp>
#include <Mod/Aplan/App/AplanPartFilter.hpp>

namespace Aplan
{
    class AplanAppExport AplanAnalysis : public App::DocumentObjectGroup
    {
        PROPERTY_HEADER(Aplan::AplanAnalysis);

    public:
        AplanAnalysis();
        virtual ~AplanAnalysis();

        std::vector<Aplan::AplanCompoundGroup *> getCompoundGroupObjects(void) const;
        std::vector<Aplan::PartFilter *> getPartFilterObjects(void) const;
        std::string getUniqueObjectLabel(const std::string &, const std::vector<std::string> & = {}) const;

        App::PropertyUUID Uid;
        App::PropertyString WorkingDir;

        virtual const char *getViewProviderName() const
        {
            return "AplanGui::ViewProviderAplanAnalysis";
        }

        PyObject *getPyObject(void);
    };

    class AplanAppExport DocumentObject : public App::DocumentObject
    {
        PROPERTY_HEADER(Aplan::DocumentObject);
    };

    typedef App::FeaturePythonT<AplanAnalysis> AplanAnalysisPython;
    typedef App::FeaturePythonT<DocumentObject> FeaturePython;
} //namespace Aplan

#endif // APLAN_APLANANALYSIS_HPP
