# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2009 Juergen Riegel <juergen.riegel@web.de>             *
# *   Copyright (c) 2021 Martijn Cramer <martijn.cramer@outlook.com>        *
# *                                                                         *
# *   This file is part of the FreeCAD CAx development system.              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307   *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "APLAN module Gui init script"
__author__ = "Martijn Cramer, Juergen Riegel"
__url__ = "https://www.freecadweb.org"


import FreeCAD
import FreeCADGui
from FreeCADGui import Workbench


class AplanWorkbench(Workbench):
    "APLAN workbench object"

    def __init__(self):
        self.__class__.Icon = FreeCAD.getResourceDir() + "Mod/Aplan/Resources/icons/APLAN_Workbench.svg"
        self.__class__.MenuText = "APLAN"
        self.__class__.ToolTip = "APLAN workbench"

    def Initialize(self):
        import Aplan
        import AplanGui
        import aplancommands.commands
    
    def Activated(self):
        try:
            from aplantools import aplanutils
            from aplanwebapp import server
            from webtest.http import StopableWSGIServer
        except ImportError as ie:
            aplanutils.missingPythonModule(str(ie.name or ""))
        self.server = StopableWSGIServer.create(server.app, port=8080, host="0.0.0.0")

    def Deactivated(self):
        self.server.shutdown()
        return

    def GetClassName(self):
        return "AplanGui::Workbench"


FreeCADGui.addWorkbench(AplanWorkbench())
