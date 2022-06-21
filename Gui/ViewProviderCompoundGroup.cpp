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

#include <Gui/ViewProviderPythonFeature.h>
#include <Mod/Aplan/Gui/ViewProviderCompoundGroup.hpp>

using namespace AplanGui;

PROPERTY_SOURCE(AplanGui::ViewProviderCompoundGroup, Gui::ViewProviderDocumentObject)

ViewProviderCompoundGroup::ViewProviderCompoundGroup()
{
}

ViewProviderCompoundGroup::~ViewProviderCompoundGroup()
{
}

std::vector<App::DocumentObject *> ViewProviderCompoundGroup::claimChildren(void) const
{
    return Gui::ViewProviderDocumentObjectGroup::claimChildren();
}

bool ViewProviderCompoundGroup::canDelete(App::DocumentObject *obj) const
{
    Q_UNUSED(obj)
    return true;
}

std::vector<std::string> ViewProviderCompoundGroup::getDisplayModes(void) const
{
    return {"CompoundGroup"};
}

void ViewProviderCompoundGroup::hide(void)
{
    Gui::ViewProviderDocumentObjectGroup::hide();
}

void ViewProviderCompoundGroup::show(void)
{
    Gui::ViewProviderDocumentObjectGroup::show();
}

bool ViewProviderCompoundGroup::setEdit(int ModNum)
{
    return ViewProviderDocumentObject::setEdit(ModNum);
}

void ViewProviderCompoundGroup::unsetEdit(int ModNum)
{
    Gui::ViewProviderDocumentObjectGroup::unsetEdit(ModNum);
}

bool ViewProviderCompoundGroup::onDelete(const std::vector<std::string> &)
{
    return true;
}

bool ViewProviderCompoundGroup::canDragObjects() const
{
    return true;
}

bool ViewProviderCompoundGroup::canDragObject(App::DocumentObject *obj) const
{
    if (!obj)
        return false;
    else if (obj->getTypeId().isDerivedFrom(Base::Type::fromName("Aplan::FeaturePython")))
        return true;
    else
        return false;
}

void ViewProviderCompoundGroup::dragObject(App::DocumentObject *obj)
{
    ViewProviderDocumentObjectGroup::dragObject(obj);
}

bool ViewProviderCompoundGroup::canDropObjects() const
{
    return true;
}

bool ViewProviderCompoundGroup::canDropObject(App::DocumentObject *obj) const
{
    return canDragObject(obj);
}

void ViewProviderCompoundGroup::dropObject(App::DocumentObject *obj)
{
    ViewProviderDocumentObjectGroup::dropObject(obj);
}

// Python feature -----------------------------------------------------------------------

namespace Gui
{
    /// @cond DOXERR
    PROPERTY_SOURCE_TEMPLATE(AplanGui::ViewProviderCompoundGroupPython, AplanGui::ViewProviderCompoundGroup)
    /// @endcond

    // explicit template instantiation
    template class AplanGuiExport ViewProviderPythonFeatureT<ViewProviderCompoundGroup>;
}