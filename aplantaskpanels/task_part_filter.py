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

__title__ = ""
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

# @package task_part_filter
#  \ingroup APLAN
#  \brief task panel for PartFilter object

from aplantools import aplanutils
try:
    import FreeCAD
    import FreeCADGui
    import itertools
    import ObjectsAplan
    from PySide2 import QtCore, QtGui, QtWidgets
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class _TaskPanel:
    """
    The TaskPanel for APLAN PartFilter object
    """
    unhighlightColor: typing.Tuple = (0.8, 0.8, 0.8, 0.0)
    unhighlightTransparencyLevel: int = 80
    highlightColorExcluded: typing.Tuple = (1.0, 0.0, 0.0, 0.0)
    transparencyLevelExcluded: int = 80
    highlightColorGrouped: typing.Tuple = (0.0, 0.0, 1.0, 0.0)
    transparencyLevelGrouped: int = 80

    def __init__(self, partFilterObject) -> None:
        self._obj = partFilterObject
        self._analysis = aplanutils.getActiveAnalysis()
        
        self._excludePartsForm = FreeCADGui.PySideUic.loadUi(
            FreeCAD.getHomePath() + "Mod/Aplan/Resources/ui/ExcludeParts.ui")
        self._groupPartsForm = FreeCADGui.PySideUic.loadUi(
            FreeCAD.getHomePath() + "Mod/Aplan/Resources/ui/GroupParts.ui")
        # Equally stretch the table widget's columns
        for i in range(self._groupPartsForm.tw_part_list.columnCount()):
            self._groupPartsForm.tw_part_list.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.Stretch)

        self.form = [self._excludePartsForm, self._groupPartsForm]
        self._model: QtGui.QStandardItemModel = QtGui.QStandardItemModel()

        self._parts: typing.Dict = {partObject.Label: partObject
                                    for partObject in FreeCAD.ActiveDocument.findObjects("Part::Feature")
                                    if not partObject.isDerivedFrom("Aplan::Compound")}
        self._partTypes: typing.Dict = {partLabel: self.__getPartType(partLabel) 
                                        for partLabel in self._parts.keys()}
        self._initialPartViews: typing.Dict = {label: {"ShapeColor":   partObject.ViewObject.ShapeColor,
                                                       "Transparency": partObject.ViewObject.Transparency}
                                               for label, partObject in self._parts.items()}

        self._compounds: typing.Dict = {compound.Label: list(compound.Links)
                                        for compound in self._obj.Compounds}     
        self._excludedParts: typing.Dict = {partObject.Label: partObject for partObject in self._obj.ExcludedParts}

        excludedPartLabels_: typing.Set[str] = set(self._excludedParts.keys())
        groupedPartLabels_: typing.Set[str] = self.__getGroupedPartLabels()
        self.__initExcludePartsForm()
        self.__initGroupPartsForm()
        self.__highlightExcludedParts(excludedPartLabels_)
        self.__highlightGroupedParts(groupedPartLabels_)
        self.__unhighlightParts(set(self._parts.keys()).difference(excludedPartLabels_).difference(groupedPartLabels_))

        # Connect Signals and Slots
        self._model.itemChanged.connect(self.__partClicked)
        QtCore.QObject.connect(
            self._groupPartsForm.btn_add_part_group,
            QtCore.SIGNAL("clicked()"),
            self.__addPartGroup
        )
        QtCore.QObject.connect(
            self._groupPartsForm.btn_remove_part_group,
            QtCore.SIGNAL("clicked()"),
            self.__removePartGroup
        )

    def getStandardButtons(self) -> int:
        button_value = int(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        return button_value

    def accept(self) -> bool:
        compounds_: typing.Set = set(itertools.chain.from_iterable([compoundGroup.Group for compoundGroup in self._analysis.CompoundGroupObjects]))
        compoundLabels_: typing.Set = {compound.Label for compound in compounds_}
        for compoundLabel_ in compoundLabels_:
            if compoundLabel_ not in self._compounds.keys():
                FreeCAD.ActiveDocument.removeObject(compoundLabel_)
        compoundObjects: typing.List = []
        for compoundLabel, components in self._compounds.items():
            if compoundLabel not in compoundLabels_:
                compoundObj = ObjectsAplan.makeCompound(self._analysis, components, compoundLabel)
                compoundObjects.append(compoundObj)
        self._obj.Compounds += compoundObjects
        for compoundGroupObject in self._analysis.CompoundGroupObjects:
            if len(compoundGroupObject.CompoundObjects) == 0:
                FreeCAD.ActiveDocument.removeObject(compoundGroupObject.Label)
        
        self._obj.ExcludedParts = self._excludedParts.values()

        self.__exit()
        return True

    def reject(self) -> bool:
        self.__exit()
        return True

    def __addPartGroup(self) -> None:
        compoundLabel: str = self._analysis.getUniqueObjectLabel("Compound", list(self._compounds.keys()))
        compoundItem: QtWidgets.QTreeWidgetItem = QtWidgets.QTreeWidgetItem([compoundLabel])
        partObjects: typing.List[str] = []

        selectedParts_: typing.List[QtWidgets.QTableWidgetItem] = self._groupPartsForm.tw_part_list.selectedItems()
        if len(selectedParts_) == 0:
            aplanutils.displayAplanError(message="Unable to create compound!", 
                                         error="A compound cannot be empty. Please, add some parts before continuing.")
        elif len(selectedParts_) == 1:
            aplanutils.displayAplanError(message="Unable to create compound!", 
                                         error="A compound cannot consist of only one part. Please, add some additional parts before continuing.")
        else:
            selectedPart_: QtWidgets.QTableWidgetItem
            for selectedPart_ in selectedParts_:
                row: int = selectedPart_.row()
                partLabel: str = self._groupPartsForm.tw_part_list.item(row, 0).text()
                partObjects.append(self._parts[partLabel])
                partItem: QtWidgets.QTreeWidgetItem = QtWidgets.QTreeWidgetItem([partLabel])
                compoundItem.addChild(partItem)
                self.__disableItemExcludePartsForm(partLabel)
                self.__disableItemGroupPartsForm(partLabel)
                self.__highlightGroupedParts({partLabel})
            self._compounds[compoundLabel] = partObjects
            self._groupPartsForm.tw_group_list.insertTopLevelItem(0, compoundItem)

    def __disableItemExcludePartsForm(self, label: str) -> None:
        items: typing.List[QtGui.QStandardItem] = self._model.findItems(label)
        item: QtGui.QStandardItem
        for item in items:
            item.setEnabled(False)
            item.setCheckState(QtCore.Qt.Unchecked)

    def __disableItemGroupPartsForm(self, label: str) -> None:
        items: typing.List[QtWidgets.QTableWidgetItem] = self._groupPartsForm.tw_part_list.findItems(label, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchCaseSensitive)
        item: QtWidgets.QTableWidgetItem
        for item in items:
            row: int = item.row()
            column: int
            for column in range(self._groupPartsForm.tw_part_list.columnCount()):
                item_: QtWidgets.QTableWidgetItem = self._groupPartsForm.tw_part_list.item(row, column)
                item_.setFlags(item_.flags() & ~QtCore.Qt.ItemIsSelectable)
                item_.setForeground(QtGui.QBrush(QtGui.QColor("lightgray")))

    def __enableItemExcludePartsForm(self, label: str) -> None:
        items: typing.List[QtGui.QStandardItem] = self._model.findItems(label)
        item: QtGui.QStandardItem
        for item in items:
            item.setEnabled(True)
            item.setCheckState(QtCore.Qt.Unchecked)

    def __enableItemGroupPartsForm(self, label: str) -> None:
        items: typing.List[QtWidgets.QTableWidgetItem] = self._groupPartsForm.tw_part_list.findItems(label, QtCore.Qt.MatchFixedString | QtCore.Qt.MatchCaseSensitive)
        item: QtWidgets.QTableWidgetItem
        for item in items:
            row: int = item.row()
            column: int
            for column in range(self._groupPartsForm.tw_part_list.columnCount()):
                item_: QtWidgets.QTableWidgetItem = self._groupPartsForm.tw_part_list.item(row, column)
                item_.setFlags(item_.flags() | QtCore.Qt.ItemIsSelectable)
                item_.setForeground(QtGui.QBrush(QtGui.QColor("black")))

    def __exit(self) -> None:
        if len(self._obj.ExcludedParts) == 0 and len(self._obj.Compounds) == 0:
            FreeCAD.ActiveDocument.removeObject(self._obj.Name)

        self.__resetPartViews()
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()

    def __getGroupedPartLabels(self) -> typing.Set[str]:
        groupedParts_: typing.Set = set(itertools.chain.from_iterable(self._compounds.values()))
        return {partObject.Label for partObject in groupedParts_}

    def __getPartType(self, partLabel: str) -> str:
        subshapesCount: int = len(self._parts[partLabel].Shape.SubShapes)
        if subshapesCount == 1:
            return "Part"
        elif subshapesCount > 1:
            return "Assembly"
        else:
            return "None"

    def __highlightExcludedParts(self, partLabels: typing.Set[str]) -> None:
        partLabel: str
        for partLabel in partLabels:
            viewObject = self._parts[partLabel].ViewObject
            viewObject.ShapeColor = _TaskPanel.highlightColorExcluded
            viewObject.Transparency = _TaskPanel.transparencyLevelExcluded

    def __highlightGroupedParts(self, partLabels: typing.Set[str]) -> None:
        partLabel: str
        for partLabel in partLabels:
            viewObject = self._parts[partLabel].ViewObject
            viewObject.ShapeColor = _TaskPanel.highlightColorGrouped
            viewObject.Transparency = _TaskPanel.transparencyLevelGrouped

    def __initExcludePartsForm(self) -> None:
        excludedPartLabels_: typing.Set[str] = set(self._excludedParts.keys())
        groupedPartLabels_: typing.Set[str] = self.__getGroupedPartLabels()
        partLabel: str
        for partLabel in self._parts.keys():
            item = QtGui.QStandardItem(partLabel)
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            if partLabel in groupedPartLabels_:
                item.setEnabled(False)
                item.setCheckable(True)
                item.setCheckState(QtCore.Qt.Unchecked)
                self.__disableItemExcludePartsForm(partLabel)
            else:
                item.setEnabled(True)
                item.setCheckable(True)
                item.setCheckState(QtCore.Qt.Checked if partLabel in excludedPartLabels_ else QtCore.Qt.Unchecked)
            self._model.appendRow(item)
        self._model.sort(QtCore.Qt.AscendingOrder)
        self._excludePartsForm.lv_part_list.setModel(self._model)

    def __initGroupPartsForm(self) -> None:
        groupedPartLabels: typing.Set[str] = self.__getGroupedPartLabels()
        self._groupPartsForm.tw_part_list.clearContents()
        self._groupPartsForm.tw_part_list.setRowCount(len(self._parts.keys()))
        for index, partLabel in enumerate(self._parts.keys()):
            partItem_: QtWidgets.QTableWidgetItem = QtWidgets.QTableWidgetItem(partLabel)
            partItem_.setFlags(partItem_.flags() & ~QtCore.Qt.ItemIsEditable)
            self._groupPartsForm.tw_part_list.setItem(index, 0, partItem_)
            partTypeItem_: QtWidgets.QTableWidgetItem = QtWidgets.QTableWidgetItem(self._partTypes[partLabel])
            partTypeItem_.setFlags(partTypeItem_.flags() & ~QtCore.Qt.ItemIsEditable)
            self._groupPartsForm.tw_part_list.setItem(index, 1, partTypeItem_)
            if partLabel in groupedPartLabels or partLabel in self._excludedParts.keys():
                self.__disableItemGroupPartsForm(partLabel)
        self._groupPartsForm.tw_part_list.sortItems(0, order=QtCore.Qt.AscendingOrder)

        compoundItems: typing.List[QtWidgets.QTreeWidgetItem] = []
        for compoundLabel, parts in self._compounds.items():
            partItems: typing.List[QtWidgets.QTreeWidgetItem] = [QtWidgets.QTreeWidgetItem([partObject.Label]) for partObject in parts]
            compoundItem: QtWidgets.QTreeWidgetItem = QtWidgets.QTreeWidgetItem([compoundLabel])
            compoundItem.addChildren(partItems)
            compoundItems.append(compoundItem)
        self._groupPartsForm.tw_group_list.insertTopLevelItems(0, compoundItems)

    def __partClicked(self, item: QtGui.QStandardItem) -> None:
        partLabel: str = item.text()
        partObject = self._parts[partLabel]
        if item.checkState() == QtCore.Qt.Checked:
            self.__disableItemGroupPartsForm(partLabel)
            self._excludedParts[partLabel] = partObject
            self.__highlightExcludedParts({partLabel})
        else:
            self.__enableItemGroupPartsForm(partLabel)
            self._excludedParts.pop(partLabel, None)
            self.__unhighlightParts({partLabel})
    
    def __removePartGroup(self) -> None:
        selectedGroups_: typing.List[QtWidgets.QTreeWidgetItem] = self._groupPartsForm.tw_group_list.selectedItems()
        selectedGroup_: QtWidgets.QTreeWidgetItem
        for selectedGroup_ in selectedGroups_:
            parentItem_: QtWidgets.QTreeWidgetItem = selectedGroup_
            if selectedGroup_.childCount() == 0:
                parentItem_ = selectedGroup_.parent()
            self._groupPartsForm.tw_group_list.takeTopLevelItem(self._groupPartsForm.tw_group_list.indexOfTopLevelItem(parentItem_))
            del self._compounds[parentItem_.text(0)]
            childIndex_: int
            for childIndex_ in range(parentItem_.childCount()):
                childItemLabel_: str = parentItem_.child(childIndex_).text(0)
                self.__enableItemGroupPartsForm(childItemLabel_)
                self.__enableItemExcludePartsForm(childItemLabel_)
                self.__unhighlightParts({childItemLabel_})

    def __resetPartViews(self):
        partLabel: str
        for partLabel, partObject in self._parts.items():
            viewObject = partObject.ViewObject
            viewObject.ShapeColor = self._initialPartViews[partLabel]["ShapeColor"]
            viewObject.Transparency = self._initialPartViews[partLabel]["Transparency"]

    def __unhighlightParts(self, partLabels: typing.Set[str]) -> None:
        partLabel: str
        for partLabel in partLabels:
            viewObject = self._parts[partLabel].ViewObject
            viewObject.ShapeColor = _TaskPanel.unhighlightColor
            viewObject.Transparency = _TaskPanel.unhighlightTransparencyLevel
