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

#include <App/Document.h>
#include <Base/Console.h>
#include <Gui/Application.h>
#include <Gui/Command.h>

//===========================================================================
// CmdAplanTest THIS IS JUST A TEST COMMAND
//===========================================================================
DEF_STD_CMD(CmdAplanTest)

CmdAplanTest::CmdAplanTest()
    : Command("APLAN_Test")
{
    sAppModule = "Aplan";
    sGroup = QT_TR_NOOP("Aplan");
    sMenuText = QT_TR_NOOP("Hello");
    sToolTipText = QT_TR_NOOP("Aplan Test function");
    sWhatsThis = "APLAN_Test";
    sStatusTip = QT_TR_NOOP("Aplan Test function");
    sPixmap = "APLAN_Test";
    sAccel = "CTRL+H";
}

void CmdAplanTest::activated(int)
{
    Base::Console().Message("Hello, World!\n");
}
//================================================================================================

void CreateAplanCommands(void)
{
    Gui::CommandManager &rcCmdMgr = Gui::Application::Instance->commandManager();

    rcCmdMgr.addCommand(new CmdAplanTest());
}
