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
        self.__exit()
        return True

    def reject(self) -> bool:
        self.__exit()
        return True

    def __addPartGroup(self) -> None:
        pass

    def __exit(self) -> None:
        FreeCADGui.ActiveDocument.resetEdit()
        FreeCAD.ActiveDocument.recompute()

    def __partClicked(self, item: QtGui.QStandardItem) -> None:
        pass

    def __removePartGroup(self) -> None:
        pass
