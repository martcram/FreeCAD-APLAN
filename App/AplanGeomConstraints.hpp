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

#ifndef APLAN_GEOMCONSTRAINTS_HPP
#define APLAN_GEOMCONSTRAINTS_HPP

#include <App/DocumentObject.h>
#include <App/FeaturePython.h>
#include <App/PropertyStandard.h>

namespace Aplan
{
    class AplanAppExport GeomConstraints : public App::DocumentObject
    {
        PROPERTY_HEADER(Aplan::GeomConstraints);

    public:
        GeomConstraints();
        virtual ~GeomConstraints();

        // Location of the JSON file representing the geometrical constraints
        App::PropertyString FileLocation;

        // Returns the type name of the ViewProvider
        const char *getViewProviderName(void) const
        {
            return "AplanGui::ViewProviderGeomConstraints";
        }
    };

    typedef App::FeaturePythonT<GeomConstraints> GeomConstraintsPython;

} // namespace Aplan

#endif // APLAN_GEOMCONSTRAINTS_HPP