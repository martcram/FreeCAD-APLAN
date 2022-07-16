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

#include <Gui/ViewProviderDocumentObject.h>
#include <Gui/ViewProviderDocumentObjectGroup.h>
#include <Gui/ViewProviderPythonFeature.h>
#include <Mod/Aplan/Gui/ViewProviderConstraintGroup.hpp>

using namespace AplanGui;

PROPERTY_SOURCE(AplanGui::ViewProviderConstraintGroup, Gui::ViewProviderDocumentObject)

ViewProviderConstraintGroup::ViewProviderConstraintGroup()
{
    sPixmap = "APLAN_ConstraintGroup.svg";
}

ViewProviderConstraintGroup::~ViewProviderConstraintGroup()
{
}

std::vector<App::DocumentObject *> ViewProviderConstraintGroup::claimChildren(void) const
{
    return Gui::ViewProviderDocumentObjectGroup::claimChildren();
}

bool ViewProviderConstraintGroup::canDelete(App::DocumentObject *obj) const
{
    Q_UNUSED(obj)
    return true;
}

std::vector<std::string> ViewProviderConstraintGroup::getDisplayModes(void) const
{
    return {"ConstraintGroup"};
}

void ViewProviderConstraintGroup::hide(void)
{
    Gui::ViewProviderDocumentObjectGroup::hide();
}

void ViewProviderConstraintGroup::show(void)
{
    Gui::ViewProviderDocumentObjectGroup::show();
}

bool ViewProviderConstraintGroup::setEdit(int ModNum)
{
    return ViewProviderDocumentObject::setEdit(ModNum);
}

void ViewProviderConstraintGroup::unsetEdit(int ModNum)
{
    Gui::ViewProviderDocumentObjectGroup::unsetEdit(ModNum);
}

bool ViewProviderConstraintGroup::onDelete(const std::vector<std::string> &)
{
    return true;
}

bool ViewProviderConstraintGroup::canDragObjects() const
{
    return true;
}

bool ViewProviderConstraintGroup::canDragObject(App::DocumentObject *obj) const
{
    if (!obj)
        return false;
    else if (obj->getTypeId().isDerivedFrom(Base::Type::fromName("Aplan::FeaturePython")))
        return true;
    else
        return false;
}

void ViewProviderConstraintGroup::dragObject(App::DocumentObject *obj)
{
    ViewProviderDocumentObjectGroup::dragObject(obj);
}

bool ViewProviderConstraintGroup::canDropObjects() const
{
    return true;
}

bool ViewProviderConstraintGroup::canDropObject(App::DocumentObject *obj) const
{
    return canDragObject(obj);
}

void ViewProviderConstraintGroup::dropObject(App::DocumentObject *obj)
{
    ViewProviderDocumentObjectGroup::dropObject(obj);
}

// Python feature -----------------------------------------------------------------------

namespace Gui
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(AplanGui::ViewProviderConstraintGroupPython, AplanGui::ViewProviderConstraintGroup)
    /// @endcond

    // explicit template instantiation
    template class AplanGuiExport ViewProviderPythonFeatureT<ViewProviderConstraintGroup>;
}