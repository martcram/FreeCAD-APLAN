# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2015 Przemo Fiszt <przemo@firszt.eu>                    *
# *   Copyright (c) 2016 Bernd Hahnebach <bernd@bimstatik.org>              *
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
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "FreeCAD APLAN command base class"
__author__ = "Martijn Cramer, Przemo Firszt, Bernd Hahnebach"
__url__ = "https://www.freecadweb.org"


from typing import Dict
import FreeCAD

if FreeCAD.GuiUp:
    import AplanGui
    import FreeCADGui
    from PySide import QtCore


class CommandManager(object):

    def __init__(self) -> None:
        self.command: str = "APLAN" + self.__class__.__name__
        self.pixmap: str = self.command
        self.menutext: str = self.__class__.__name__.lstrip("_")
        self.accel: str = ""
        self.tooltip: str = "Creates a {}".format(self.menutext)
        self.resources: Dict = {}

        self.is_active: str = ""

    def GetResources(self) -> Dict:
        if self.resources == {}:
            self.resources = {
                "Pixmap": self.pixmap, "MenuText": QtCore.QT_TRANSLATE_NOOP(self.command, self.menutext),
                "Accel": self.accel, "ToolTip": QtCore.QT_TRANSLATE_NOOP(self.command, self.tooltip)
            }
        return self.resources

    def IsActive(self) -> bool:
        active: bool = False
        if self.is_active == "":
            active = False
        elif self.is_active == "always":
            active = True
        elif self.is_active == "with_document":
            active = FreeCADGui.ActiveDocument is not None
        elif self.is_active == "with_analysis":
            active = (
                AplanGui.getActiveAnalysis() is not None
                and self.active_analysis_in_active_doc()
            )
        elif self.is_active == "with_compounds":
            active = (
                AplanGui.getActiveAnalysis() is not None
                and self.active_analysis_in_active_doc()
                and (self.compoundsPresent())
            )
        return active

    def Activated(self):
        if self.do_activated == "add_obj_on_gui_noset_edit":
            self.add_obj_on_gui_noset_edit(self.__class__.__name__.lstrip("_"))
        elif self.do_activated == "add_obj_on_gui_set_edit":
            self.add_obj_on_gui_set_edit(self.__class__.__name__.lstrip("_"))
        # in all other cases Activated is implemented it the command class

    def active_analysis_in_active_doc(self) -> bool:
        analysis = AplanGui.getActiveAnalysis()
        if analysis.Document is FreeCAD.ActiveDocument:
            self.active_analysis = analysis
            return True
        else:
            return False

    def compoundsPresent(self) -> bool:
        analysis = AplanGui.getActiveAnalysis()
        for group in analysis.CompoundGroupObjects:
            if len(group.Group) > 0:
                return True
        return False

    # ****************************************************************************************
    # methods to add the objects to the document in FreeCADGui mode

    def add_obj_on_gui_set_edit(self, obj_type):
        FreeCAD.ActiveDocument.openTransaction(
            "Create Aplan{}"
            .format(obj_type)
        )
        FreeCADGui.addModule(
            "ObjectsAplan"
        )
        FreeCADGui.addModule(
            "AplanGui"
        )
        FreeCADGui.doCommand(
            "AplanGui.getActiveAnalysis().addObject(ObjectsAplan."
            "make{}(FreeCAD.ActiveDocument))"
            .format(obj_type)
        )
        # no other obj should be selected if we go in task panel
        FreeCADGui.Selection.clearSelection()
        FreeCADGui.doCommand(
            "FreeCADGui.ActiveDocument.setEdit(FreeCAD.ActiveDocument.ActiveObject.Name)"
        )
        FreeCAD.ActiveDocument.recompute()

    def add_obj_on_gui_noset_edit(self, obj_type) -> None:
        FreeCAD.ActiveDocument.openTransaction(
            "Create Aplan{}"
            .format(obj_type)
        )
        FreeCADGui.addModule(
            "ObjectsAplan"
        )
        FreeCADGui.addModule(
            "AplanGui"
        )
        FreeCADGui.doCommand(
            "AplanGui.getActiveAnalysis().addObject(ObjectsAplan."
            "make{}(FreeCAD.ActiveDocument))"
            .format(obj_type)
        )
        # no clear selection is done
        FreeCAD.ActiveDocument.recompute()
