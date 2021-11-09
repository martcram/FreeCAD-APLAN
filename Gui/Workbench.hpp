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

#ifndef APLAN_WORKBENCH_HPP
#define APLAN_WORKBENCH_HPP

#include <Gui/Workbench.h>

namespace AplanGui
{

    class AplanGuiExport Workbench : public Gui::StdWorkbench
    {
        TYPESYSTEM_HEADER();

    public:
        Workbench();
        virtual ~Workbench();

        // Run some actions when the workbench gets activated.
        virtual void activated();
        // Run some actions when the workbench gets deactivated.
        virtual void deactivated();

    protected:
        Gui::MenuItem *setupMenuBar() const;
        Gui::ToolBarItem *setupToolBars() const;
    };

} // namespace AplanGui

#endif // APLAN_WORKBENCH_HPP
