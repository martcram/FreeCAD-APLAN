# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
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

__title__ = "Task panel for APLAN GeomConstraints object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

# @package task_geom_constraints
#  \ingroup APLAN
#  \brief task panel for APLAN GeomConstraints object

import FreeCAD
import FreeCADGui
from aplantools import aplanutils
from aplanwebapp import api, browser
try:
    import json
    from PySide2 import QtCore, QtWidgets
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class _TaskPanel:
    """
    The TaskPanel for APLAN GeomConstraints object
    """

    def __init__(self, geomConstraintsObject) -> None:
        self._obj = geomConstraintsObject
        self._analysis = aplanutils.getActiveAnalysis()
        self._animations: bool = True
        api.toggleAnimations(self._animations)
        self._motionDirection: str = self._obj.MotionDirection

        self.form = FreeCADGui.PySideUic.loadUi(
            FreeCAD.getHomePath() + "Mod/Aplan/Resources/ui/GeomConstraints.ui")

        # Equally stretch the table widget's columns
        for i in range(self.form.tw_constraints_list.columnCount()):
            self.form.tw_constraints_list.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self._parts: typing.Dict = {partObject.Label: partObject
                                    for partObject in FreeCAD.ActiveDocument.findObjects("Part::Feature")}
        self._initialPartViews: typing.Dict = {label: {"ShapeColor":   part.ViewObject.ShapeColor,
                                                       "Transparency": part.ViewObject.Transparency,
                                                       "Visibility":   part.ViewObject.Visibility}
                                               for label, part in self._parts.items()}

        self._compounds: typing.Dict = {compoundGroup.Label: compoundGroup.Group for compoundGroup in self._analysis.CompoundGroupObjects}
        self._excludedParts: typing.Dict = {excludedPart.Label: excludedPart for partFilter in self._analysis.PartFilterObjects 
                                            for excludedPart in partFilter.ExcludedParts}

        self._prevObstructions: typing.Set[typing.Tuple] = set()

        webServerThread: QtCore.QTimer = QtCore.QTimer(self.form)
        webServerThread.timeout.connect(self.__callWebServer)
        webServerThread.start(100)

        index: int
        motionDirection: str
        for index, motionDirection in enumerate(aplanutils.getPropertyEnumerationValues(self._obj, "MotionDirection")):
            self.form.cb_motion_direction.insertItem(index, motionDirection)
        self.form.cb_motion_direction.setCurrentText(self._motionDirection)

        obstructions: typing.Set[typing.Tuple] = set()
        self.__resetConstraintsTable(obstructions)
        self.form.l_constraints.setText(str(len(obstructions)))

        # Connect Signals and Slots
        self.form.cb_animations.stateChanged.connect(self.__toggleAnimations)
        self.form.cb_motion_direction.currentTextChanged.connect(self.__switchMotionDirection)

    def getStandardButtons(self) -> int:
        button_value = int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        return button_value

    def accept(self) -> bool:
        self.__saveObstructionGraph(self._obj.FileLocation)
        self.__writeProperties()
        self.__exit()
        return True

    def reject(self) -> bool:
        self.__exit()
        return True
    
    def __callWebServer(self) -> None:
        # Check if the set of obstructions has been changed
        obstructions: typing.Set[typing.Tuple] = api.getObstructionGraphEdges()
        if obstructions and self._prevObstructions != obstructions:
            self.__resetConstraintsTable(obstructions)
            self.form.l_constraints.setText(str(len(obstructions)))
            self._prevObstructions = obstructions

    def __exit(self) -> None:
        browser.hide()
        api.clearCacheObstructionGraph()

        self._obj.ViewObject.Document.resetEdit()
        self._obj.Document.recompute()

    def __resetConstraintsTable(self, obstructions: typing.Set[typing.Tuple]) -> None:
        self.form.tw_constraints_list.clearContents()
        self.form.tw_constraints_list.setRowCount(len(obstructions))
        for index, connection in enumerate(obstructions):
            self.form.tw_constraints_list.setItem(index, 0, QtWidgets.QTableWidgetItem(connection[0]))
            self.form.tw_constraints_list.setItem(index, 1, QtWidgets.QTableWidgetItem(connection[1]))
        self.form.tw_constraints_list.sortItems(0, order=QtCore.Qt.SortOrder.AscendingOrder)

    def __saveObstructionGraph(self, fileLocation: str) -> None:
        with open(fileLocation, 'w') as file:
            json.dump(api.getObstructionGraph(), file)

    def __switchMotionDirection(self, motionDirection: str) -> None:
        self._motionDirection = motionDirection

    def __toggleAnimations(self, state: QtCore.Qt.CheckState) -> None:
        if state == QtCore.Qt.Checked:
            self._animations = True
        else:
            self._animations = False
        api.toggleAnimations(self._animations)
    
    def __writeProperties(self) -> None:
        self._obj.MotionDirection = self._motionDirection
