/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2008 Werner Mayer <werner.wm.mayer@gmx.de>              *
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
 *   Suite 330, Boston, MA 02111-1307, USA                                 *
 *                                                                         *
 ***************************************************************************/

#include "PreCompiled.hpp"

#ifndef _PreComp_
#include <qobject.h>
#endif

#include <Gui/MenuManager.h>
#include <Gui/ToolBarManager.h>

#include "ActiveAnalysisObserver.hpp"
#include "Workbench.hpp"

using namespace AplanGui;

#if 0 // needed for Qt's lupdate utility
    qApp->translate("Workbench", "APLAN");
    qApp->translate("Workbench", "&APLAN");
    //
    qApp->translate("Workbench", "Model");
    qApp->translate("Workbench", "M&odel");
#endif

/// @namespace AplanGui @class Workbench
TYPESYSTEM_SOURCE(AplanGui::Workbench, Gui::StdWorkbench)

Workbench::Workbench()
{
}

Workbench::~Workbench()
{
}

void Workbench::activated()
{
    Gui::Workbench::activated();
}

void Workbench::deactivated()
{
    AplanGui::ActiveAnalysisObserver::instance()->unsetActiveObject();
    Gui::Workbench::deactivated();
}

Gui::MenuItem *Workbench::setupMenuBar() const
{
    Gui::MenuItem *root = StdWorkbench::setupMenuBar();
    Gui::MenuItem *item = root->findItem("&Windows");

    Gui::MenuItem *model = new Gui::MenuItem;
    root->insertItem(item, model);
    model->setCommand("M&odel");
    *model << "APLAN_Analysis"
           << "Separator";

    return root;
}

Gui::ToolBarItem *Workbench::setupToolBars() const
{
    Gui::ToolBarItem *root = StdWorkbench::setupToolBars();

    Gui::ToolBarItem *model = new Gui::ToolBarItem(root);
    model->setCommand("Model");
    *model << "APLAN_Analysis"
           << "Separator"
           << "APLAN_ToggleTransparency"
           << "APLAN_TopoConstraints";

    Gui::ToolBarItem *partFilters = new Gui::ToolBarItem(root);
    partFilters->setCommand("Part filters");
    *partFilters
        << "APLAN_PartFilter";

    return root;
}
