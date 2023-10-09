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

__title__ = "Task panel for APLAN TopoConstraints object"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

# @package task_topo_constraints
#  \ingroup APLAN
#  \brief task panel for APLAN TopoConstraints object

from aplantools import aplanutils
try:
    from aplanwebapp import api, browser
    import FreeCAD
    import FreeCADGui
    import json
    from PySide2 import QtCore, QtWidgets
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class _TaskPanel:
    """
    The TaskPanel for APLAN TopoConstraints object
    """
    defaultShapeColor: typing.Tuple = (0.5, 0.5, 0.5, 0.0)
    defaultTransparency: int = 0
    highlightColor: typing.Tuple = (1.0, 0.0, 0.0, 0.0)
    transparencyLevel: int = 80

    def __init__(self, topoConstraintsObject) -> None:
        self._obj = topoConstraintsObject
        self._analysis = aplanutils.getActiveAnalysis()
        self._animations: bool = True
        api.toggleAnimations(self._animations)

        self.form = FreeCADGui.PySideUic.loadUi(
            FreeCAD.getHomePath() + "Mod/Aplan/Resources/ui/TopoConstraints.ui")

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

        self._prevSelectedConnections: typing.Dict = {}
        self._prevConnections: typing.Set[typing.Tuple] = set()

        webServerThread: QtCore.QTimer = QtCore.QTimer(self.form)
        webServerThread.timeout.connect(self.__callWebServer)
        webServerThread.start(100)

        # Connect Signals and Slots
        self.form.cb_animations.stateChanged.connect(self.__toggleAnimations)

    def getStandardButtons(self) -> int:
        button_value = int(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        return button_value

    def accept(self) -> bool:
        self.__saveConnectionGraph(self._obj.FileLocation)
        self.__exit()
        return True

    def reject(self) -> bool:
        self.__exit()
        return True

    def __callWebServer(self) -> None:
        # Check if the set of selected connections has been changed
        selectedConnections: typing.Dict = api.getSelectedConnections()
        if selectedConnections and self._prevSelectedConnections != selectedConnections:
            self.__highlightTopoConstraints({selectedConnections["source"]: selectedConnections["targets"]})
            self._prevSelectedConnections = selectedConnections

        # Check if the set of connections has been changed
        connections: typing.Set[typing.Tuple] = api.getConnectionGraphEdges()
        if connections and self._prevConnections != connections:
            self.__resetConstraintsTable(connections)
            self.form.l_constraints.setText(str(len(connections)))
            self._prevConnections = connections
    
    def __exit(self) -> None:
        browser.hide()
        api.clearCacheConnectionGraph()
        self.__resetPartViews()

        self._obj.ViewObject.Document.resetEdit()
        self._obj.Document.recompute()

    def __highlightTopoConstraints(self, topoConstraints: typing.Dict[str, typing.List[str]]) -> None:
        involvedParts_: typing.Set[str] = set()
        sourceComponentLabel: str
        targetComponentLabels: typing.List[str]
        for sourceComponentLabel, targetComponentLabels in topoConstraints.items():
            targetComponents_: typing.Set = set()
            if sourceComponentLabel in self._compounds.keys():
                for part in self._compounds[sourceComponentLabel]:
                    if part.Label not in self._excludedParts.keys():
                        targetComponents_.add(part)
            elif sourceComponentLabel not in self._excludedParts.keys():
                targetComponents_.add(self._parts[sourceComponentLabel])
            
            if self._animations:
                involvedParts_.add(sourceComponentLabel)
                involvedParts_.update(targetComponentLabels)
                for partLabel in set(self._parts.keys()).difference(involvedParts_):
                    self._parts[partLabel].ViewObject.Visibility = False

                for component in targetComponents_:
                    parts_: typing.List = [component]
                    if component.isDerivedFrom("Aplan::Compound"):
                        parts_ = component.Links
                    for part_ in parts_:
                        part_.ViewObject.ShapeColor = _TaskPanel.highlightColor
                        part_.ViewObject.Transparency = 0
                        part_.ViewObject.Visibility = True

            targetComponentLabel: str
            for targetComponentLabel in targetComponentLabels:
                targetComponents: typing.Set = set()
                if targetComponentLabel in self._compounds.keys():
                    for part in self._compounds[targetComponentLabel]:
                        if part.Label not in self._excludedParts.keys():
                            targetComponents.add(part)
                elif targetComponentLabel not in self._excludedParts.keys():
                    targetComponents.add(self._parts[targetComponentLabel])
                
                if self._animations:
                    for component in targetComponents:
                        parts: typing.List = [component]
                        if component.isDerivedFrom("Aplan::Compound"):
                            parts = component.Links
                        for part in parts:
                            part.ViewObject.ShapeColor = self._initialPartViews[part.Label]["ShapeColor"]
                            part.ViewObject.Transparency = 80
                            part.ViewObject.Visibility = True

    def __resetConstraintsTable(self, connections: typing.Set[typing.Tuple]) -> None:
        self.form.tw_constraints_list.clearContents()
        self.form.tw_constraints_list.setRowCount(len(connections))
        for index, connection in enumerate(connections):
            self.form.tw_constraints_list.setItem(index, 0, QtWidgets.QTableWidgetItem(connection[0]))
            self.form.tw_constraints_list.setItem(index, 1, QtWidgets.QTableWidgetItem(connection[1]))
        self.form.tw_constraints_list.sortItems(0, order=QtCore.Qt.SortOrder.AscendingOrder)

    def __resetPartViews(self) -> None:
        for component in self._parts.values():
            parts: typing.List = [component]
            if component.isDerivedFrom("Aplan::Compound"):
                parts = component.Links
            for part in parts:
                part.ViewObject.ShapeColor = self._initialPartViews[part.Label]["ShapeColor"]
                part.ViewObject.Transparency = self._initialPartViews[part.Label]["Transparency"]
                part.ViewObject.Visibility = self._initialPartViews[part.Label]["Visibility"]

    def __saveConnectionGraph(self, fileLocation: str) -> None:
        with open(fileLocation, 'w') as file:
            json.dump(api.getConnectionGraph(), file)

    def __toggleAnimations(self, state: QtCore.Qt.CheckState) -> None:
        if state == QtCore.Qt.Checked:
            self._animations = True
        else:
            self._animations = False
            self.__resetPartViews()
        api.toggleAnimations(self._animations)
