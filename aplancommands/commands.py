# ***************************************************************************
# *                                                                         *
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

__title__ = "FreeCAD APLAN command definitions"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

from .manager import CommandManager
import FreeCAD
if FreeCAD.GuiUp:
    import AplanGui
    import FreeCADGui
    from FreeCAD import Qt

# Python command definitions
# For C++ command definitions is referred to src/Mod/Aplan/Command.cpp


class _ConnectionDetectorSwellOCCT(CommandManager):
    "..."

    def __init__(self) -> None:
        super(_ConnectionDetectorSwellOCCT, self).__init__()
        self.pixmap: str = "APLAN_ConnectionDetector"
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "APLAN_ConnectionDetectorSwellOCCT",
            "SwellOCCT connection detector"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "APLAN_ConnectionDetectorSwellOCCT",
            "Creates a SwellOCCT solver for detecting part connections\nbased on bounding box intersections and OpenCascade's tools"
        )
        self.do_activated = "add_obj_on_gui_set_edit"

    def IsActive(self) -> bool:
        analysis = AplanGui.getActiveAnalysis()
        objectExists: bool = any([detector.Type == "SwellOCCT"
                                  for detector in analysis.ConnectionDetectorObjects])
        return (analysis is not None
                and self.active_analysis_in_active_doc()
                and not objectExists)


class _PartFilter(CommandManager):
    "..."

    def __init__(self) -> None:
        super(_PartFilter, self).__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "APLAN_PartFilter",
            "Part filter"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "APLAN_PartFilter",
            "Creates a part filter for grouping or exluding parts from analysis"
        )
        self.do_activated = "add_obj_on_gui_set_edit"
    
    def IsActive(self) -> bool:
        analysis = AplanGui.getActiveAnalysis()
        return (analysis is not None
                and self.active_analysis_in_active_doc()
                and len(analysis.PartFilterObjects) == 0)


class _ToggleTransparency(CommandManager):
    "Toggles the transparency of the available parts"

    def __init__(self):
        super(_ToggleTransparency, self).__init__()
        self.menutext: str = "Toggle transparency"
        self.accel: str = "CTRL+T"
        self.tooltip: str = "Toggles the transparency of the available parts"
        self.is_active: str = "with_document"

    def Activated(self):
        parts = FreeCAD.ActiveDocument.findObjects("Part::Feature")
        if sum([True for part in parts if part.ViewObject.Transparency > 0]) >= len(parts)/2:
            for part in parts:
                part.ViewObject.Transparency = 0
        else:
            for part in parts:
                part.ViewObject.Transparency = 80


class _TopoConstraints(CommandManager):
    "Computes the topological constraints of the selected parts"

    def __init__(self):
        super(_TopoConstraints, self).__init__()
        self.menutext = Qt.QT_TRANSLATE_NOOP(
            "APLAN_TopoConstraints",
            "Topological constraints"
        )
        self.tooltip = Qt.QT_TRANSLATE_NOOP(
            "APLAN_TopoConstraints",
            "Computes the topological constraints of the selected parts"
        )
        self.is_active = "with_analysis"
        self.do_activated = "add_obj_on_gui_set_edit"


FreeCADGui.addCommand("APLAN_ConnectionDetectorSwellOCCT", _ConnectionDetectorSwellOCCT())
FreeCADGui.addCommand("APLAN_PartFilter",                  _PartFilter())
FreeCADGui.addCommand("APLAN_ToggleTransparency",          _ToggleTransparency())
FreeCADGui.addCommand("APLAN_TopoConstraints",             _TopoConstraints())
