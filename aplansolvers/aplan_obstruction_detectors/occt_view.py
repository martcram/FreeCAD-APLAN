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

__title__ = "FreeCAD APLAN OCCT obstruction detector's view classes"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

import FreeCAD
import FreeCADGui
import aplansolvers.aplan_obstruction_detectors.base_obstruction_detector as base
import aplansolvers.aplan_obstruction_detectors.base_view_obstruction_detector as baseView
import aplansolvers.aplan_obstruction_detectors.occt as occt
import ObjectsAplan
from aplantools import aplanutils
try:
    import itertools
    import json
    import math
    import os
    from PySide2 import QtCore, QtWidgets
    import signal
    import subprocess
    import sys
    import time
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class VPOCCT(baseView.IVPObstructionDetector):
    def getIcon(self):
        """
        Return the icon in XMP format which will appear in the tree view. 
        This method is optional and if not defined a default icon is shown.
        """
        return ":/icons/APLAN_ObstructionDetectorOCCT.svg"

    def setEdit(self, vobj, mode=0):
        task = _TaskPanel(vobj.Object)
        FreeCADGui.Control.showDialog(task)
        return True

    def unsetEdit(self, vobj, mode=0):
        FreeCADGui.Control.closeDialog()
        return True

    def doubleClicked(self, vobj):
        guidoc = FreeCADGui.getDocument(vobj.Object.Document)
        # check if another VP is in edit mode
        # https://forum.freecadweb.org/viewtopic.php?t=13077#p104702
        if not guidoc.getInEdit():
            guidoc.setEdit(vobj.Object.Name)
        else:
            message = "Active Task Dialog found! Please close this one before opening a new one!"
            QtWidgets.QMessageBox.critical(None, "Error in tree view", message)
            FreeCAD.Console.PrintError(message + "\n")
        return True


class _TaskPanel(baseView.ITaskPanel):
    """
    The TaskPanel for APLAN ConnectionDetectorSwellOCCT object
    """

    def __init__(self, swellOCCTObject) -> None:
        super(_TaskPanel, self).__init__(swellOCCTObject)

        # Read and/or calculate property values
        #* General properties
        self._parts: typing.Dict = {part.Label: part for part in FreeCAD.ActiveDocument.findObjects("Part::Feature")}
        self._excludedPartsDict: typing.Dict = {}
        self._noExcludedParts: int = 0
        self._compoundsDict: typing.Dict = {}
        self._noCompounds: int = 0
        if self._analysis.PartFilterObjects:
            self._excludedPartsDict = {excludedPart.Label: excludedPart for partFilter in self._analysis.PartFilterObjects 
                                       for excludedPart in partFilter.ExcludedParts}
            self._noExcludedParts = len(self._excludedPartsDict)
            self._compoundsDict = {compound.Label: compound for partFilter in self._analysis.PartFilterObjects 
                                   for compound in partFilter.Compounds}
            self._noCompounds = len(self._compoundsDict)
        excludedPartLabels: typing.Set[str] = set(self._excludedPartsDict.keys())
        compoundsLabels: typing.Set[str] = set(self._compoundsDict.keys())
        groupedPartLabels: typing.Set[str] = {part.Label for compound in self._compoundsDict.values() for part in compound.Links}
        self._disjointPartsDict: typing.Dict = {disjointPartLabel: self._parts[disjointPartLabel] 
                                                for disjointPartLabel in set(self._parts.keys()).difference(
                                                    excludedPartLabels.union(groupedPartLabels).union(compoundsLabels))}
        disjointPartLabels: typing.Set[str] = set(self._disjointPartsDict.keys())
        self._noDisjointParts: int = len(disjointPartLabels)
        self._noParts: int = len(disjointPartLabels) + len(excludedPartLabels) + len(groupedPartLabels)
        self._componentsDict: typing.Dict = {**self._disjointPartsDict, **self._compoundsDict}
        self._computationTime: float = 0.0
        self._initPlacementsDict: typing.Dict = {componentLabel: component.Placement for componentLabel, component in self._componentsDict.items()}
        #* Refinement properties
        for refinementMethod in occt.RefinementMethod:
            if self.obj.RefinementMethod == refinementMethod.value[0]:
                self._refinementMethod: occt.RefinementMethod = refinementMethod
                break
        self._configParamRefinement: typing.Dict[occt.RefinementMethod, typing.Set[str]] = {}
        self._qWidgetDictRefinement: typing.Dict[str, typing.Dict] = {}
        #* Solver properties
        self._variableStepSizeEnabled: bool = bool(self.obj.VariableStepSizeEnabled)
        self._stepSizeCoefficient: float = float(self.obj.StepSizeCoefficient)
        self._minStepSize: float = float(self.obj.MinStepSize)
        self._fixedStepSize: float = float(self.obj.FixedStepSize)
        self._motionDirections: typing.Set[base.CartesianMotionDirection] = {base.CartesianMotionDirection[motionDir.upper()]
                                                                             for motionDir in self.obj.MotionDirections}
        for solverMethod in occt.SolverMethod:
            if self.obj.SolverMethod == solverMethod.value[0]:
                self._solverMethod: occt.SolverMethod = solverMethod
                break
        self._minDistance: float = float(self.obj.MinDistance)
        self._overlapTolerance: float = float(self.obj.OverlapTolerance)
        self._classificationTolerance: float = float(self.obj.ClassificationTolerance)
        self._volumeTolerance: float = float(self.obj.VolumeTolerance)
        self._sampleCoefficient: float = float(self.obj.SampleCoefficient)
        self._configParamSolver: typing.Dict[occt.SolverMethod, typing.Set[str]] = {occt.SolverMethod.DistToShape:   {"overlapTolerance", "minDistance", "classificationTolerance"},
                                                                                    occt.SolverMethod.MeshInside:    {"overlapTolerance", "classificationTolerance", "sampleCoefficient"},
                                                                                    occt.SolverMethod.GeoDataInside: {"overlapTolerance", "classificationTolerance", "sampleCoefficient"},
                                                                                    occt.SolverMethod.Common:        {"overlapTolerance", "volumeTolerance"},
                                                                                    occt.SolverMethod.Fuse:          {"overlapTolerance", "volumeTolerance"}}
        self._qWidgetDictSolver: typing.Dict[str, typing.Dict] = {"classificationTolerance": {"label": self.form.l_label_classification_tolerance,
                                                                                              "value": self.form.dsb_classification_tolerance},
                                                                  "minDistance": {"label": self.form.l_label_min_distance, 
                                                                                  "value": self.form.dsb_min_distance},
                                                                  "overlapTolerance": {"label": self.form.l_label_overlap_tolerance,
                                                                                       "value": self.form.dsb_overlap_tolerance},
                                                                  "sampleCoefficient": {"label": self.form.l_label_sample_coefficient, 
                                                                                        "value": self.form.dsb_sample_coefficient},
                                                                  "volumeTolerance": {"label": self.form.l_label_volume_tolerance, 
                                                                                      "value": self.form.dsb_volume_tolerance}}
        self._multiprocessingEnabled: bool = bool(self.obj.MultiprocessingEnabled)
        self._linearDeflection: float = float(self.obj.LinearDeflection)

        # Update task panel form
        #* General properties
        self.form.l_label_parts.setToolTip(
            "The total amount of parts in this document.")
        self.form.l_parts.setText(str(self._noParts))
        self.form.l_label_disjoint_parts.setToolTip(
            "The amount of parts that are not compounded/grouped i.e. disjointed.")
        self.form.l_disjoint_parts.setText(str(self._noDisjointParts))
        self.form.l_label_compounds.setToolTip(
            "The amount of compounds created in this analysis container.")
        self.form.l_compounds.setText(str(self._noCompounds))
        self.form.l_label_excluded_parts.setToolTip(
            "The amount of parts that were excluded from analysis.")
        self.form.l_excluded_parts.setText(str(self._noExcludedParts))
        self.form.l_label_type.setToolTip(
            "The type of solver selected for detecting part connections.")
        self.form.l_type.setText(self._solverType)
        #* Refinement properties
        index1: int
        for index1, refinementMethod in enumerate(occt.RefinementMethod):
            self.form.cb_refinement_method.insertItem(index1, refinementMethod.value[0])
            self.form.cb_refinement_method.setItemData(index1, refinementMethod.value[1], QtCore.Qt.ToolTipRole)
        self.__switchRefinementMethod(self._refinementMethod.value[0])
        self.form.cb_refinement_method.setCurrentText(self._refinementMethod.value[0])
        #* Solver properties
        self.form.cb_variable_step_size.setChecked(self._variableStepSizeEnabled)
        self.__toggleVariableStepSize((QtCore.Qt.Unchecked, QtCore.Qt.Checked)[self._variableStepSizeEnabled])
        self.form.dsb_step_size_coeff.setValue(self._stepSizeCoefficient)
        self.form.dsb_min_step_size.setValue(self._minStepSize)
        self.form.dsb_fixed_step_size.setValue(self._fixedStepSize)
        index2: int
        for index2, solverMethod in enumerate(occt.SolverMethod):
            self.form.cb_solver_method.insertItem(index2, solverMethod.value[0])
            self.form.cb_solver_method.setItemData(index2, solverMethod.value[1], QtCore.Qt.ToolTipRole)
        self.__switchSolverMethod(self._solverMethod.value[0])
        self.form.cb_solver_method.setCurrentText(self._solverMethod.value[0])
        motionDir_: base.CartesianMotionDirection
        for motionDir_ in self._motionDirections:
            self.form.findChild(QtWidgets.QCheckBox,
                                "cb_{}".format(motionDir_.name.lower())).setChecked(True)
        self.form.cb_multiprocessing.setChecked(self._multiprocessingEnabled)
        self.__toggleMultiprocessing((QtCore.Qt.Unchecked, QtCore.Qt.Checked)[self._multiprocessingEnabled])
        self.form.dsb_linear_deflection.setValue(self._linearDeflection)
        self.form.l_time.setText("{} s".format(self._computationTime))

        # Connect signals and slots
        #* Refinement properties
        self.form.cb_refinement_method.currentTextChanged.connect(self.__switchRefinementMethod)
        for qWidget in {widgets["value"] for widgets in self._qWidgetDictRefinement.values()}:
            qWidget.valueChanged.connect(self.__readConfigFieldsRefinement)
        #* Solver properties
        self.form.cb_variable_step_size.stateChanged.connect(self.__toggleVariableStepSize)
        self.form.dsb_step_size_coeff.valueChanged.connect(self.__readInputFields)
        self.form.dsb_min_step_size.valueChanged.connect(self.__readInputFields)
        self.form.dsb_fixed_step_size.valueChanged.connect(self.__readInputFields)
        self.form.cb_solver_method.currentTextChanged.connect(self.__switchSolverMethod)
        for qWidget in {widgets["value"] for widgets in self._qWidgetDictSolver.values()}:
            qWidget.valueChanged.connect(self.__readConfigFieldsSolver)
        motionDirection_: base.CartesianMotionDirection
        for motionDirection_ in self._motionDirections:
            self.form.findChild(QtWidgets.QCheckBox,
                                "cb_{}".format(motionDirection_.name.lower())
                                ).stateChanged.connect(lambda state, objName=motionDirection_.name: 
                                                       self.__readCheckBoxState(state, objName))
        self.form.btn_run.clicked.connect(self.__run)
        self.form.cb_multiprocessing.stateChanged.connect(self.__toggleMultiprocessing)
        self.form.dsb_linear_deflection.valueChanged.connect(self.__readInputFields)

    def getStandardButtons(self) -> int:
        button_value = int(QtWidgets.QDialogButtonBox.Cancel)
        return button_value

    def reject(self) -> bool:
        if self._solverThread is not None and self._solverThread.isRunning():
            QtWidgets.QMessageBox.critical(FreeCADGui.getMainWindow(), "Running solver", 
            "The solver is still running! Please terminate it before continuing.")
            return False

        self.__writeProperties()
        self.obj.ViewObject.Document.resetEdit()
        self.obj.Document.recompute()
        return True

    def __handleError(self, error: typing.Tuple) -> None:
        aplanutils.displayAplanError(*error)

    def __processOutput(self, output: typing.Dict) -> None:
        self._computationTime = round(output.get("time", 0.0), 3)
        self.form.l_time.setText("{} s".format(self._computationTime))
        results: typing.Dict[base.CartesianMotionDirection, typing.Set[typing.Tuple[str, str]]] = output.get("constraints", {})
        
        motionDirection: base.CartesianMotionDirection
        for motionDirection in self._motionDirections:
            geomConstraints: typing.Set[typing.Tuple[str, str]] = set()
            if motionDirection in results.keys():
                geomConstraints = results[motionDirection]
            else:
                oppositeMotionDirection: base.CartesianMotionDirection = base.CartesianMotionDirection(abs(motionDirection.value))
                geomConstraints = {constraint[::-1] for constraint in results.get(oppositeMotionDirection, set())}
            ObjectsAplan.makeGeomConstraints(self._analysis, motionDirection, geomConstraints, "GeomConstraints_{}".format(motionDirection.name))

    def __readCheckBoxState(self, state: int, objectName: str) -> None:
        motionDirection: base.CartesianMotionDirection = base.CartesianMotionDirection[objectName.upper()]
        if state == QtCore.Qt.Checked:
            self._motionDirections.add(motionDirection)
        else:
            self._motionDirections.remove(motionDirection)

    def __readConfigFieldsRefinement(self) -> None:
        paramLabel: str
        for paramLabel, qWidgets in self._qWidgetDictRefinement.items():
            self.__dict__["_{}".format(paramLabel)] = qWidgets["value"].value()

    def __readConfigFieldsSolver(self) -> None:
        paramLabel: str
        for paramLabel, qWidgets in self._qWidgetDictSolver.items():
            self.__dict__["_{}".format(paramLabel)] = qWidgets["value"].value()

    def __readInputFields(self) -> None:
        self._stepSizeCoefficient = float(self.form.dsb_step_size_coeff.text().replace(',', '.'))
        self._minStepSize = float(self.form.dsb_min_step_size.text().replace(',', '.'))
        self._fixedStepSize = float(self.form.dsb_fixed_step_size.text().replace(',', '.'))
        self._linearDeflection = float(self.form.dsb_linear_deflection.text().replace(',', '.'))

    def __reportProgress(self, progress: typing.Dict) -> None:
        self.form.te_output.setTextColor(baseView.MessageType(progress["type"]).value)
        self.form.te_output.append(progress["msg"])
        self.form.te_output.setTextColor(baseView.MessageType.INFO.value)

    def __resetInitialPlacements(self) -> None:
        for component in self._componentsDict.values():
            component.Placement = self._initPlacementsDict[component.Label]

    def __run(self) -> None:
        if self._solverThread is None or not self._solverThread.isRunning():
            # Init
            configParamRefinement: typing.Dict = {param: self.__dict__["_{}".format(param)] 
                                                  for param in self._configParamRefinement.get(self._refinementMethod, set())}
            configParamSolver: typing.Dict = {param: self.__dict__["_{}".format(param)] 
                                              for param in self._configParamSolver.get(self._solverMethod, set())}
            configParamSolverGeneral: typing.Dict = {"variableStepSizeEnabled": self._variableStepSizeEnabled,
                                                     "stepSizeCoefficient": self._stepSizeCoefficient,
                                                     "minStepSize": self._minStepSize,
                                                     "fixedStepSize": self._fixedStepSize}
            inputParams: typing.Dict = {"componentsDict": self._componentsDict,
                                        "refinementMethod": self._refinementMethod,
                                        "configParamRefinement": configParamRefinement,
                                        "solverMethod": self._solverMethod,
                                        "configParamSolver": configParamSolver,
                                        "configParamSolverGeneral": configParamSolverGeneral,
                                        "motionDirections": self._motionDirections,
                                        "multiprocessingEnabled": self._multiprocessingEnabled,
                                        "linearDeflection": self._linearDeflection}
            self._solverThread = QtCore.QThread()
            self._worker: Worker = Worker(self.obj.Type, inputParams)
            self._worker.moveToThread(self._solverThread)

            # Connect signals and slots
            self._solverThread.started.connect(self._worker.run)
            self._solverThread.finished.connect(self.__threadFinished)
            self._solverThread.finished.connect(self._solverThread.deleteLater)
            self._worker.progress.connect(self.__reportProgress)
            self._worker.finished.connect(self.__processOutput)
            self._worker.finished.connect(self._solverThread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            self._worker.error.connect(self.__handleError)
            # QtCore.Qt.BlockingQueuedConnection: Wait for a SLOT to finish its execution
            self._worker.movePart.connect(self.__movePart, QtCore.Qt.BlockingQueuedConnection)
            self._worker.setPlacement.connect(self.__setPartPlacement, QtCore.Qt.BlockingQueuedConnection)

            # Start solver thread
            self._solverThread.start()
            self.__threadStarted()

        elif self._solverThread is not None and self._solverThread.isRunning() and self._worker.isRunning:
            self.form.btn_run.setText("Terminating ...")
            self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_TERMINATING))

            self._worker.stop()
            self._solverThread.quit()

    def __switchSolverMethod(self, solverMethod: str) -> None:
        for method in occt.SolverMethod:
            if solverMethod == method.value[0]:
                self._solverMethod = method
                break
        for qWidget in set(itertools.chain.from_iterable([widgets.values() for widgets in self._qWidgetDictSolver.values()])):
            qWidget.setHidden(True)
        param_: str
        for param_ in self._configParamSolver.get(self._solverMethod, set()):
            self._qWidgetDictSolver[param_]["value"].setValue(self.__dict__["_{}".format(param_)])
            for qWidget in self._qWidgetDictSolver[param_].values():
                qWidget.setHidden(False)

    def __switchRefinementMethod(self, refinementMethod: str) -> None:
        for method in occt.RefinementMethod:
            if refinementMethod == method.value[0]:
                self._refinementMethod = method
                break
        for qWidget in set(itertools.chain.from_iterable([widgets.values() for widgets in self._qWidgetDictRefinement.values()])):
            qWidget.setHidden(True)
        param_: str
        for param_ in self._configParamRefinement.get(self._refinementMethod, set()):
            self._qWidgetDictRefinement[param_]["value"].setValue(self.__dict__["_{}".format(param_)])
            for qWidget in self._qWidgetDictRefinement[param_].values():
                qWidget.setHidden(False)
        
        if self._refinementMethod == occt.RefinementMethod.None_:
            self.form.l_label_variable_step_size.setEnabled(False)
            self.form.cb_variable_step_size.setEnabled(False)
            self.form.cb_variable_step_size.setCheckState(QtCore.Qt.Unchecked)
            self.__toggleVariableStepSize(QtCore.Qt.Unchecked)
        elif self._refinementMethod == occt.RefinementMethod.BoundBox:
            self.form.l_label_variable_step_size.setEnabled(True)
            self.form.cb_variable_step_size.setEnabled(True)

    def __threadFinished(self) -> None:
        self.form.btn_run.setText("Run")
        self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_RUN))
        self._solverThread = None
        self.__resetInitialPlacements()

    def __threadStarted(self) -> None:
        self.form.btn_run.setText("Abort")
        self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_ABORT))

    def __toggleMultiprocessing(self, state: QtCore.Qt.CheckState) -> None:
        self._multiprocessingEnabled = (state == QtCore.Qt.Checked)
        if self._multiprocessingEnabled:
            self.form.l_label_linear_deflection.setHidden(False)
            self.form.dsb_linear_deflection.setHidden(False)
        else:
            self.form.l_label_linear_deflection.setHidden(True)
            self.form.dsb_linear_deflection.setHidden(True)

    def __toggleVariableStepSize(self, state: QtCore.Qt.CheckState) -> None:
        self._variableStepSizeEnabled = (state == QtCore.Qt.Checked)
        if self._variableStepSizeEnabled:
            self.form.l_label_step_size_coeff.setHidden(False)
            self.form.dsb_step_size_coeff.setHidden(False)
            self.form.l_label_min_step_size.setHidden(False)
            self.form.dsb_min_step_size.setHidden(False)
            self.form.l_label_fixed_step_size.setHidden(True)
            self.form.dsb_fixed_step_size.setHidden(True)
        else:
            self.form.l_label_step_size_coeff.setHidden(True)
            self.form.dsb_step_size_coeff.setHidden(True)
            self.form.l_label_min_step_size.setHidden(True)
            self.form.dsb_min_step_size.setHidden(True)
            self.form.l_label_fixed_step_size.setHidden(False)
            self.form.dsb_fixed_step_size.setHidden(False)

    def __writeProperties(self) -> None:
        self.obj.RefinementMethod = self._refinementMethod.value[0]
        self.obj.VariableStepSizeEnabled = self._variableStepSizeEnabled
        self.obj.StepSizeCoefficient = self._stepSizeCoefficient
        self.obj.MinStepSize = self._minStepSize
        self.obj.FixedStepSize = self._fixedStepSize
        self.obj.SolverMethod = self._solverMethod.value[0]
        self.obj.MinDistance = self._minDistance
        self.obj.ClassificationTolerance = self._classificationTolerance
        self.obj.OverlapTolerance = self._overlapTolerance
        self.obj.VolumeTolerance = self._volumeTolerance
        self.obj.SampleCoefficient = self._sampleCoefficient
        self.obj.MotionDirections = [motionDir.name for motionDir in self._motionDirections]
        self.obj.MultiprocessingEnabled = self._multiprocessingEnabled
        self.obj.LinearDeflection = self._linearDeflection

    def __movePart(self, inputParams: typing.Dict) -> None:
        part = inputParams["part"]
        displVector = inputParams["vector"]
        part.Placement.move(displVector)

    def __setPartPlacement(self, inputParams: typing.Dict) -> None:
        part = inputParams["part"]
        baseVector = inputParams.get("baseVector", part.Placement.Base)
        rotationVector = inputParams.get("rotationVector", part.Placement.Rotation)
        part.Placement = FreeCAD.Placement(baseVector, rotationVector)


class Worker(baseView.BaseWorker):
    movePart: QtCore.Signal = QtCore.Signal(dict)
    setPlacement: QtCore.Signal = QtCore.Signal(dict)

    def __init__(self, detectorType: str, inputParams: typing.Dict) -> None:
        super(Worker, self).__init__(detectorType)
        self._inputParams: typing.Dict = inputParams
        self._isRunning: bool = False
        self._componentsDict: typing.Dict = self._inputParams["componentsDict"]
        self._refinementMethod: occt.RefinementMethod = self._inputParams["refinementMethod"]
        self._configParamRefinement: typing.Dict = self._inputParams["configParamRefinement"]
        self._solverMethod: occt.SolverMethod = self._inputParams["solverMethod"]
        self._configParamSolver: typing.Dict = self._inputParams["configParamSolver"]
        self._configParamSolverGeneral: typing.Dict = self._inputParams["configParamSolverGeneral"]
        self._motionDirections: typing.Set[base.CartesianMotionDirection] = self._inputParams["motionDirections"]
        self._multiprocessingEnabled: bool = self._inputParams["multiprocessingEnabled"]
        self._linearDeflection: float = self._inputParams["linearDeflection"]

    def run(self) -> None:
        self.progress.emit({"msg": ">>> STARTED",
                            "type": baseView.MessageType.INFO})
        self._isRunning = True
        computationTime: float = 0.0
        solverTime: float = 0.0

        try:
            geometricalConstraints: typing.Dict[base.CartesianMotionDirection, typing.Set[typing.Tuple[str, str]]] = {}
            if self._multiprocessingEnabled:
                self.progress.emit({"msg": "====== Multiprocessing ======",
                                    "type": baseView.MessageType.INFO})
                self.progress.emit({"msg": "Performing the {} refinement method\nand the {} solver method".format(self._refinementMethod.value[0],
                                                                                                                  self._solverMethod.value[0]),
                                    "type": baseView.MessageType.INFO})
                output: typing.Dict[base.CartesianMotionDirection, typing.Tuple[typing.Set[typing.Tuple[str, str]], float]]= self.multiprocess()
                computationTimes: typing.List[float] = []

                motionDir: base.CartesianMotionDirection
                geomConstraints: typing.Tuple[typing.Set[typing.Tuple[str, str]], float]
                for motionDir, geomConstraints in output.items():
                    geometricalConstraints[motionDir] = geomConstraints[0]
                    computationTimes.append(geomConstraints[1])
                    self.progress.emit({"msg": "\t{}: FOUND {} GEOMETRICAL CONSTRAINT(S)".format(motionDir.name.upper(), len(geomConstraints[0])),
                                        "type": baseView.MessageType.FOCUS})
                    
                    fileReadable: bool
                    missingConstraints: typing.Set[str, str] = {}
                    excessConstraints: typing.Set[str, str] = {}
                    groundTruthPath: str = '/'.join(FreeCAD.ActiveDocument.FileName.split('/')[:-1] + ["GroundTruth", "GeomConstraints_" + motionDir.name.upper() + ".json"])
                    fileReadable, missingConstraints, excessConstraints = self.__checkConstraintsCorrectness(groundTruthPath, geomConstraints[0], motionDir)
                    if fileReadable:
                        noMissingConstraints: int = len(missingConstraints)
                        noExcessConstraints: int = len(excessConstraints)
                        if noMissingConstraints > 0:
                            self.progress.emit({"msg": "\t> {} missing constraint(s) w.r.t. ground truth data".format(noMissingConstraints),
                                                "type": baseView.MessageType.WARNING})
                        if noExcessConstraints > 0:
                            self.progress.emit({"msg": "\t> {} excess constraint(s) w.r.t. ground truth data".format(noExcessConstraints),
                                                "type": baseView.MessageType.WARNING})

                    self.progress.emit({"msg": "\t> Done: {:.3f}s".format(geomConstraints[1]),
                                        "type": baseView.MessageType.INFO})
                if computationTimes:
                    computationTime = max(computationTimes)
            else:
                self._solver: occt.OCCTSolver = occt.OCCTSolver(self._componentsDict.values(), 
                                                                self._motionDirections)

                self.progress.emit({"msg": "====== Refining ======",
                                    "type": baseView.MessageType.INFO})
                self.progress.emit({"msg": "Performing the {} refinement method".format(self._refinementMethod.value[0]),
                                    "type": baseView.MessageType.INFO})
                time0: float = time.perf_counter()

                intervalObstructionsDict: typing.Dict = self._solver.refine(self._refinementMethod, 
                                                                            self._configParamRefinement)

                time1: float = time.perf_counter()
                computationTime += time1-time0

                noCollisionChecks: int = 0
                if self._refinementMethod == occt.RefinementMethod.None_:
                    noCollisionChecks = self.__maxNoCollisionChecks(intervalObstructionsDict, self._configParamSolverGeneral["fixedStepSize"])
                elif self._refinementMethod == occt.RefinementMethod.BoundBox:
                    noCollisionChecks = self.__maxNoCollisionChecksRefinement(intervalObstructionsDict, self._configParamSolverGeneral["stepSizeCoefficient"], self._configParamSolverGeneral["minStepSize"])

                noPotentialObstructions: int = 0
                motionDirection: base.CartesianMotionDirection
                targetDict: typing.Dict
                for motionDirection, targetDict in intervalObstructionsDict.items():
                    self.progress.emit({"msg": "*** Motion direction: {} ***".format(motionDirection.name),
                                        "type": baseView.MessageType.INFO})
                    targetLabel: str
                    intervalObstructionsPairs: typing.List
                    for targetLabel, intervalObstructionsPairs in targetDict.items():
                        noObstructionComponents: int = len(set(itertools.chain.from_iterable([pair[1] for pair in intervalObstructionsPairs])))
                        noPotentialObstructions += noObstructionComponents
                        self.progress.emit({"msg": "\tFound {} potential obstructions for {}.".format(noObstructionComponents, targetLabel),
                                            "type": baseView.MessageType.INFO})
                self.progress.emit({"msg": "*******\nFound {} potential obstructions in total.".format(noPotentialObstructions),
                                    "type": baseView.MessageType.INFO})
                self.progress.emit({"msg": "Maximum number of collision checks: {}.".format(noCollisionChecks),
                                    "type": baseView.MessageType.INFO})
                self.progress.emit({"msg": "> Done: {:.3f}s".format(time1-time0),
                                    "type": baseView.MessageType.INFO})

                if not self._isRunning:
                    self.__abort()
                    return

                self.progress.emit({"msg": "====== Solving =======",
                                    "type": baseView.MessageType.INFO})
                self.progress.emit({"msg": "Performing the {} solver method".format(self._solverMethod.value[0]),
                                    "type": baseView.MessageType.INFO})
                time2: float = time.perf_counter()

                geometricalConstraints = self._solver.solve(self._solverMethod, 
                                                            self._configParamSolver, 
                                                            self._configParamSolverGeneral,
                                                            intervalObstructionsDict=intervalObstructionsDict,
                                                            fMovePart=self.__movePart,
                                                            fSetPartPlacement=self.__setPartPlacement)

                time3: float = time.perf_counter()
                solverTime = time3-time2
                computationTime += solverTime

                motionDir_: base.CartesianMotionDirection
                geomConstraints_: typing.Set[typing.Tuple[str, str]]
                for motionDir_, geomConstraints_ in geometricalConstraints.items():
                    self.progress.emit({"msg": "\t{}: FOUND {} GEOMETRICAL CONSTRAINT(S)".format(motionDir_.name.upper(), len(geomConstraints_)),
                                        "type": baseView.MessageType.FOCUS})

                    fileReadable: bool
                    missingConstraints: typing.Set[str, str] = {}
                    excessConstraints: typing.Set[str, str] = {}
                    groundTruthPath: str = '/'.join(FreeCAD.ActiveDocument.FileName.split('/')[:-1] + ["GroundTruth", "GeomConstraints_" + motionDir_.name.upper() + ".json"])
                    fileReadable, missingConstraints, excessConstraints = self.__checkConstraintsCorrectness(groundTruthPath, geomConstraints_, motionDir_)
                    if fileReadable:
                        noMissingConstraints: int = len(missingConstraints)
                        noExcessConstraints: int = len(excessConstraints)
                        if noMissingConstraints > 0:
                            self.progress.emit({"msg": "\t> {} missing constraint(s) w.r.t. ground truth data".format(noMissingConstraints),
                                                "type": baseView.MessageType.WARNING})
                        if noExcessConstraints > 0:
                            self.progress.emit({"msg": "\t> {} excess constraint(s) w.r.t. ground truth data".format(noExcessConstraints),
                                                "type": baseView.MessageType.WARNING})
                    
                self.progress.emit({"msg": "> Done: {:.3f}s".format(solverTime),
                                    "type": baseView.MessageType.INFO})

            if not self._isRunning:
                self.__abort()
                return

            self.progress.emit({"msg": ">>> FINISHED",
                                "type": baseView.MessageType.INFO})

            self._isRunning = False
            self.finished.emit({"time": computationTime,
                                "constraints": geometricalConstraints})
        
        except Exception as e:
            self.progress.emit({"msg": ">>> ERROR\n{}\nERROR <<<".format(e),
                                "type": baseView.MessageType.ERROR})
            self.__abort()
  
    def multiprocess(self) -> typing.Dict[base.CartesianMotionDirection, typing.Tuple[typing.Set[typing.Tuple[str, str]], float]]:
        geometricalConstraints: typing.Dict[base.CartesianMotionDirection, typing.Tuple[typing.Set[typing.Tuple[str, str]], float]] = {}

        MULTIPROC_SCRIPT_PATH: typing.Final[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                                                "{}_multiproc.py".format(self._detectorType.lower()))
        FREECAD_PYTHON_PATH: typing.Optional[str] = os.getenv("FREECAD_PYTHON_PATH")
        if FREECAD_PYTHON_PATH:
            sys.path.append(FREECAD_PYTHON_PATH)
            cmd = [FREECAD_PYTHON_PATH, MULTIPROC_SCRIPT_PATH,
                   "--file_path", str(FreeCAD.ActiveDocument.FileName),
                   "--component_labels", str(list(self._componentsDict.keys())),
                   "--motion_directions", str([m.value for m in self._motionDirections]),
                   "--linear_deflection", str(self._linearDeflection),
                   "--refinement_method", self._refinementMethod.name,
                   "--config_param_refinement", json.dumps(self._configParamRefinement),
                   "--solver_method", self._solverMethod.name,
                   "--config_param_solver", json.dumps(self._configParamSolver),
                   "--config_param_solver_general", json.dumps(self._configParamSolverGeneral)]

            self._subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid)
            output: bytes = self._subprocess.communicate()[0]

            if self._isRunning:
                subprocessReturn: typing.Dict[int, typing.Tuple[typing.Set[typing.Tuple[str, str]], float]] = eval(output.decode("utf-8"))

                motionDirValue: int
                result: typing.Tuple[typing.Set[typing.Tuple[str, str]], float]
                for motionDirValue, result in subprocessReturn.items():
                    geometricalConstraints[base.CartesianMotionDirection(motionDirValue)] = result
        else:
            geometricalConstraints = {motionDirection: (set(), 0.0) for motionDirection in self._motionDirections}
            aplanutils.displayAplanError("Missing environment variable!",
                                         "Please add FREECAD_PYTHON_PATH (i.e. the path of the Python executable FreeCAD was built with) to your machine's environment variables.")
        return geometricalConstraints

    def stop(self) -> None:
        self._isRunning = False
        if self._multiprocessingEnabled:
            if self._subprocess.poll() is None:
                os.killpg(os.getpgid(self._subprocess.pid), signal.SIGTERM)
        else:
            self._solver.stop()

    def __movePart(self, target, vector) -> None:
        self.movePart.emit({"part": target, "vector": vector})

    def __setPartPlacement(self, target, baseVector, rotationVector) -> None:
        self.setPlacement.emit({"part": target, "baseVector": baseVector, "rotationVector": rotationVector})

    def __abort(self) -> None:
        self.stop()
        self.progress.emit({"msg": ">>> ABORTED",
                            "type": baseView.MessageType.WARNING})
        self.finished.emit({})

    def __maxNoCollisionChecks(self, intervalObstructionsDict: typing.Dict, fixedStepSize: float) -> int:
        noChecks: int = 0
        targetDict: typing.Dict
        for _, targetDict in intervalObstructionsDict.items():
            intervalObstructionsPairs: typing.List
            for intervalObstructionsPairs in targetDict.values():
                pair: typing.Tuple
                for pair in intervalObstructionsPairs:
                    intervalLength = pair[0][1]-pair[0][0]
                    noChecks += math.floor(intervalLength/fixedStepSize) * len(self._componentsDict.keys())-1
        return noChecks

    def __maxNoCollisionChecksRefinement(self, intervalObstructionsDict: typing.Dict, stepSizeCoefficient: float, minStepSize: float) -> int:
        noChecksRefinement: int = 0
        targetDict: typing.Dict
        for _, targetDict in intervalObstructionsDict.items():
            intervalObstructionsPairs: typing.List
            for intervalObstructionsPairs in targetDict.values():
                pair: typing.Tuple
                for pair in intervalObstructionsPairs:
                    intervalLength = pair[0][1]-pair[0][0]
                    stepSize = max(intervalLength * stepSizeCoefficient, minStepSize)
                    noChecksRefinement += math.floor(intervalLength/stepSize) * len(pair[1])
        return noChecksRefinement
    
    def __checkConstraintsCorrectness(self, groundTruthPath: str, geometricalConstraints: typing.Set[typing.Tuple[str, str]], motionDirection: base.CartesianMotionDirection) -> typing.Tuple[bool, typing.Set, typing.Set]:
        fileReadable: bool = False
        missingConstraints: typing.Set[str, str] = {}
        excessConstraints: typing.Set[str, str] = {}

        if os.path.isfile(groundTruthPath) and os.access(groundTruthPath, os.R_OK):
            fileReadable = True
            with open(groundTruthPath) as jsonFile:
                groundTruth = json.load(jsonFile)
                groundTruthConstraints: typing.Set[typing.Tuple[str, str]] = {(link["source"], link["target"]) for link in groundTruth["links"]}
                missingConstraints = groundTruthConstraints.difference(geometricalConstraints)
                excessConstraints = geometricalConstraints.difference(groundTruthConstraints)

                outputPath: str = '/'.join(FreeCAD.ActiveDocument.FileName.split('/')[:-1] + ["GroundTruth", "CorrectnessCheck_" + motionDirection.name.upper() + ".json"])
                with open(outputPath, 'w') as f:
                    output: typing.Dict[str, typing.Set[typing.Tuple[str, str]]] = {"missing": list(missingConstraints), "excess": list(excessConstraints)}
                    json.dump(output, f)

                return True, missingConstraints, excessConstraints
        
        return fileReadable, missingConstraints, excessConstraints