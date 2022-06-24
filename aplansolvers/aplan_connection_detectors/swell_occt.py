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

__title__ = "FreeCAD APLAN SwellOCCT connection detector"
__author__ = "Martijn Cramer"
__url__ = "https://www.freecadweb.org"

from aplantools import aplanutils
try:
    import Aplan
    import aplansolvers.aplan_connection_detectors.base_connection_detector as base
    import enum
    import FreeCAD
    import FreeCADGui
    import itertools
    import MeshPart
    from PySide2 import QtCore, QtWidgets
    import time
    import typing
except ImportError as ie:
    aplanutils.missingPythonModule(str(ie.name or ""))


class RefinementMethod(enum.Enum):
    None_ = ("None", "")
    BoundBox = ("BoundBox_Intersection", "Tooltip information about this refinement method")


class SolverMethod(enum.Enum):
    DistToShape   = ("BRepExtrema_DistShapeShape", "Tooltip information about this solver method")
    MeshInside    = ("BRepMesh_SolidClassifier",   "Tooltip information about this solver method")
    GeoDataInside = ("GeoData_SolidClassifier",    "Tooltip information about this solver method")
    Proximity     = ("BRepExtrema_ShapeProximity", "Tooltip information about this solver method")
    Section       = ("BRepAlgoAPI_Section",        "Tooltip information about this solver method")


def create(doc, name: str = "SwellOCCT"):
    return aplanutils.createObject(doc, name, SwellOCCT, VPSwellOCCT)


class SwellOCCT(base.IConnectionDetector):
    def __init__(self, obj):
        super(SwellOCCT, self).__init__(obj)
        obj.Proxy = self
        self.addProperties(obj)

    def addProperties(self, obj):
        if hasattr(obj, "Type"):
            obj.Type = self.__class__.__name__

        if not hasattr(obj, "RefinementMethod"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "RefinementMethod",
                "Connection detector",
                "..."
            )
            obj.RefinementMethod = [method.value[0] for method in RefinementMethod]

        if not hasattr(obj, "SwellDistance"):
            obj.addProperty(
                "App::PropertyFloat",
                "SwellDistance",
                "Connection detector",
                "..."
            )
            obj.SwellDistance = 0.01

        if not hasattr(obj, "SolverMethod"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "SolverMethod",
                "Connection detector",
                "..."
            )
            obj.SolverMethod = [method.value[0] for method in SolverMethod]
        
        if not hasattr(obj, "SampleRate"):
            obj.addProperty(
                "App::PropertyFloat",
                "SampleRate",
                "Connection detector",
                "..."
            )
            obj.SampleRate = 0.01

        if not hasattr(obj, "Tolerance"):
            obj.addProperty(
                "App::PropertyFloat",
                "Tolerance",
                "Connection detector",
                "..."
            )
            obj.Tolerance = 0.00001
        
        if not hasattr(obj, "MinDistance"):
            obj.addProperty(
                "App::PropertyFloat",
                "MinDistance",
                "Connection detector",
                "..."
            )
            obj.MinDistance = 0.00001


class VPSwellOCCT(base.IVPConnectionDetector):
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


class _TaskPanel(base.ITaskPanel):
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
        #* Refinement properties
        for refinementMethod in RefinementMethod:
            if self.obj.RefinementMethod == refinementMethod.value[0]:
                self._refinementMethod: RefinementMethod = refinementMethod
                break
        self._swellDistance: float = float(self.obj.SwellDistance)
        self._configParamRefinement: typing.Dict[RefinementMethod, typing.Set[str]] = {RefinementMethod.BoundBox: {"swellDistance"}}
        self._qWidgetDictRefinement: typing.Dict[str, typing.Dict] = {"swellDistance": {"label": self.form.l_label_swell_distance, 
                                                                                        "value": self.form.dsb_swell_distance}}
        #* Solver properties
        for solverMethod in SolverMethod:
            if self.obj.SolverMethod == solverMethod.value[0]:
                self._solverMethod: SolverMethod = solverMethod
                break
        self._minDistance: float = float(self.obj.MinDistance)
        self._sampleRate: float = float(self.obj.SampleRate)
        self._tolerance: float = float(self.obj.Tolerance)
        self._configParamSolver: typing.Dict[SolverMethod, typing.Set[str]] = {SolverMethod.DistToShape:   {"minDistance"},
                                                                               SolverMethod.MeshInside:    {"sampleRate", "tolerance"},
                                                                               SolverMethod.GeoDataInside: {"sampleRate", "tolerance"},
                                                                               SolverMethod.Proximity:     {"tolerance"}}
        self._qWidgetDictSolver: typing.Dict[str, typing.Dict] = {"tolerance":   {"label": self.form.l_label_tolerance,
                                                                                  "value": self.form.dsb_tolerance},
                                                                  "minDistance": {"label": self.form.l_label_min_distance, 
                                                                                  "value": self.form.dsb_min_distance},
                                                                  "sampleRate":  {"label": self.form.l_label_sample_rate, 
                                                                                  "value": self.form.dsb_sample_rate}}

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
        for index1, refinementMethod in enumerate(RefinementMethod):
            self.form.cb_refinement_method.insertItem(index1, refinementMethod.value[0])
            self.form.cb_refinement_method.setItemData(index1, refinementMethod.value[1], QtCore.Qt.ToolTipRole)
        self.__switchRefinementMethod(self._refinementMethod.value[0])
        self.form.cb_refinement_method.setCurrentText(self._refinementMethod.value[0])
        #* Solver properties
        index2: int
        for index2, solverMethod in enumerate(SolverMethod):
            self.form.cb_solver_method.insertItem(index2, solverMethod.value[0])
            self.form.cb_solver_method.setItemData(index2, solverMethod.value[1], QtCore.Qt.ToolTipRole)
        self.__switchSolverMethod(self._solverMethod.value[0])
        self.form.cb_solver_method.setCurrentText(self._solverMethod.value[0])
        self.form.l_time.setText("{} s".format(self._computationTime))

        # Connect signals and slots
        #* Refinement properties
        self.form.cb_refinement_method.currentTextChanged.connect(self.__switchRefinementMethod)
        for qWidget in {widgets["value"] for widgets in self._qWidgetDictRefinement.values()}:
            qWidget.valueChanged.connect(self.__readConfigFieldsRefinement)
        #* Solver properties
        self.form.cb_solver_method.currentTextChanged.connect(self.__switchSolverMethod)
        for qWidget in {widgets["value"] for widgets in self._qWidgetDictSolver.values()}:
            qWidget.valueChanged.connect(self.__readConfigFieldsSolver)
        self.form.btn_run.clicked.connect(self.__run)

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
    
    def __processOutput(self, output: typing.Dict) -> None:
        self._computationTime = round(output.get("time", 0.0), 3)
        self.form.l_time.setText("{} s".format(self._computationTime))
        topoConstraints: typing.Set[str] = output.get("constraints", {})
        if len(topoConstraints) > 0:
            #TODO: add topological constraints object to active analysis
            pass 

    def __readConfigFieldsRefinement(self) -> None:
        paramLabel: str
        for paramLabel, qWidgets in self._qWidgetDictRefinement.items():
            self.__dict__["_{}".format(paramLabel)] = qWidgets["value"].value()

    def __readConfigFieldsSolver(self) -> None:
        paramLabel: str
        for paramLabel, qWidgets in self._qWidgetDictSolver.items():
            self.__dict__["_{}".format(paramLabel)] = qWidgets["value"].value()

    def __reportProgress(self, progress: typing.Dict) -> None:
        self.form.te_output.setTextColor(base.MessageType(progress["type"]).value)
        self.form.te_output.append(progress["msg"])
        self.form.te_output.setTextColor(base.MessageType.INFO.value)

    def __run(self) -> None:
        if self._solverThread is None or not self._solverThread.isRunning():
            # Init
            configParamRefinement: typing.Dict = {param: self.__dict__["_{}".format(param)] 
                                                  for param in self._configParamRefinement.get(self._refinementMethod, set())}
            configParamSolver: typing.Dict = {param: self.__dict__["_{}".format(param)] 
                                              for param in self._configParamSolver.get(self._solverMethod, set())}
            inputParams: typing.Dict = {"componentsDict": self._componentsDict,
                                        "refinementMethod": self._refinementMethod,
                                        "configParamRefinement": configParamRefinement,
                                        "solverMethod": self._solverMethod,
                                        "configParamSolver": configParamSolver}
            self._solverThread = QtCore.QThread()
            self._worker: Worker = Worker(inputParams)
            self._worker.moveToThread(self._solverThread)

            # Connect signals and slots
            self._solverThread.started.connect(self._worker.run)
            self._solverThread.finished.connect(self.__threadFinished)
            self._solverThread.finished.connect(self._solverThread.deleteLater)
            self._worker.progress.connect(self.__reportProgress)
            self._worker.finished.connect(self.__processOutput)
            self._worker.finished.connect(self._solverThread.quit)
            self._worker.finished.connect(self._worker.deleteLater)
            
            # Start solver thread
            self._solverThread.start()
            self.__threadStarted()
            
        elif self._solverThread is not None and self._solverThread.isRunning() and self._worker.isRunning:
            self.form.btn_run.setText("Terminating ...")
            self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_TERMINATING))

            self._worker.stop()
            self._solverThread.quit()

    def __switchSolverMethod(self, solverMethod: str) -> None:
        for method in SolverMethod:
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
        for method in RefinementMethod:
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

    def __threadFinished(self) -> None:
        self.form.btn_run.setText("Run")
        self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_RUN))
        self._solverThread = None

    def __threadStarted(self) -> None:
        self.form.btn_run.setText("Abort")
        self.form.btn_run.setStyleSheet("background-color: {}".format(self._COLOR_ABORT))

    def __writeProperties(self) -> None:
        self.obj.RefinementMethod = self._refinementMethod.value[0]
        self.obj.SwellDistance = self._swellDistance
        self.obj.SolverMethod = self._solverMethod.value[0]
        self.obj.MinDistance = self._minDistance
        self.obj.SampleRate = self._sampleRate
        self.obj.Tolerance = self._tolerance


class SwellOCCTSolver:
    def __init__(self, components: typing.List) -> None:
        self.setComponents(components)

    def setComponents(self, components: typing.List) -> None:
        self._componentsDict = {component.Label: component for component in components}

    def refine(self, method: RefinementMethod, configParam: typing.Dict) -> typing.List:
        potentialConnections: typing.List = []
        if method == RefinementMethod.None_:
            potentialConnections = [comb for comb in itertools.combinations(self._componentsDict.keys(), 2)]
        elif method == RefinementMethod.BoundBox:
            swellDistance: float = float(configParam["swellDistance"])
            boundBoxDict: typing.Dict = {component.Label: FreeCAD.BoundBox((component.Shape.BoundBox.XMin-swellDistance/2),
                                                                           (component.Shape.BoundBox.YMin-swellDistance/2),
                                                                           (component.Shape.BoundBox.ZMin-swellDistance/2),
                                                                           (component.Shape.BoundBox.XMax+swellDistance/2),
                                                                           (component.Shape.BoundBox.YMax+swellDistance/2),
                                                                           (component.Shape.BoundBox.ZMax+swellDistance/2))
                                        for component in self._componentsDict.values()}
            potentialConnections = [comb for comb in itertools.combinations(boundBoxDict.keys(), 2) 
                                    if boundBoxDict[comb[0]].intersect(boundBoxDict[comb[1]])]
        return potentialConnections
    
    def solve(self, method: SolverMethod, configParam: typing.Dict, **kwargs) -> typing.Set[typing.Tuple]:
        potentialConnections: typing.List = kwargs.get("potConnections", list(itertools.combinations(self._componentsDict.keys(), 2)))
        partPointsMeshDict: typing.Dict = {}
        partPointsSampleDict: typing.Dict = {}

        topologicalConstraints: typing.Set[typing.Tuple] = set()
        for potentialConnection in potentialConnections:
            componentLabel1: str = potentialConnection[0]
            componentLabel2: str = potentialConnection[1]
            component1 = self._componentsDict[potentialConnection[0]]
            component2 = self._componentsDict[potentialConnection[1]]

            if method == SolverMethod.DistToShape:
                if component1.Shape.distToShape(component2.Shape)[0] < float(configParam["minDistance"]):
                    topologicalConstraints.add(tuple(sorted([componentLabel1, componentLabel2])))
            elif method == SolverMethod.MeshInside:
                smallestComponent, largestComponent = sorted([component1, component2], key=lambda c: c.Shape.Volume, reverse=False)
                boundBox = smallestComponent.Shape.BoundBox
                maxLength: float = min(boundBox.XLength, boundBox.YLength, boundBox.ZLength) * float(configParam["sampleRate"])
                meshPoints: typing.List = []
                if smallestComponent.Label not in partPointsMeshDict.keys():
                    partPointsMeshDict[smallestComponent.Label] = MeshPart.meshFromShape(Shape=smallestComponent.Shape, MaxLength=maxLength).Points
                meshPoints = partPointsMeshDict[smallestComponent.Label]
                for p in meshPoints:
                    if largestComponent.Shape.isInside(FreeCAD.Vector(p.x, p.y, p.z), float(configParam["tolerance"]), True):
                        topologicalConstraints.add(tuple(sorted([componentLabel1, componentLabel2])))
                        break
            elif method == SolverMethod.GeoDataInside:
                smallestComponent, largestComponent = sorted([component1, component2], key=lambda c: c.Shape.Volume, reverse=False)
                boundBox = smallestComponent.Shape.BoundBox
                distance: float = min(boundBox.XLength, boundBox.YLength, boundBox.ZLength) * float(configParam["sampleRate"])
                samplePoints: typing.List = []
                if smallestComponent.Label not in partPointsSampleDict.keys():
                    partPointsSampleDict[smallestComponent.Label] = Aplan.pointSampleShape(smallestComponent.Label, distance)
                samplePoints = partPointsSampleDict[smallestComponent.Label]
                p_: typing.Tuple[float, float, float]
                for p_ in samplePoints:
                    if largestComponent.Shape.isInside(FreeCAD.Vector(p_[0], p_[1], p_[2]), float(configParam["tolerance"]), True):
                        topologicalConstraints.add(tuple(sorted([componentLabel1, componentLabel2])))
                        break
            elif method == SolverMethod.Proximity:
                overlappedSubShapes0, overlappedSubShapes1 = component1.Shape.proximity(component2.Shape, float(configParam["tolerance"]))
                if len(overlappedSubShapes0) > 0 or len(overlappedSubShapes1) > 0:
                    topologicalConstraints.add(tuple(sorted([componentLabel1, componentLabel2])))
            elif method == SolverMethod.Section:
                if len(component1.Shape.section(component2.Shape, False).Vertexes) > 0:
                    topologicalConstraints.add(tuple(sorted([componentLabel1, componentLabel2])))
        
        return topologicalConstraints


class Worker(base.BaseWorker):
    def __init__(self, inputParams: typing.Dict) -> None:
        super(Worker, self).__init__()
        self._inputParams: typing.Dict = inputParams

    def run(self) -> None:
        self.progress.emit({"msg": ">>> STARTED",
                            "type": base.MessageType.INFO})
        self._isRunning = True
        computationTime: float = 0.0

        try:
            componentsDict: typing.Dict = self._inputParams["componentsDict"]
            refinementMethod: RefinementMethod = self._inputParams["refinementMethod"]
            configParamRefinement: typing.Dict = self._inputParams["configParamRefinement"]
            solverMethod: SolverMethod = self._inputParams["solverMethod"]
            configParamSolver: typing.Dict = self._inputParams["configParamSolver"]
            solver: SwellOCCTSolver = SwellOCCTSolver(list(componentsDict.values()))
            
            self.progress.emit({"msg": "====== Refining ======",
                                "type": base.MessageType.INFO})
            self.progress.emit({"msg": "Performing the {} refinement method".format(refinementMethod.value[0]),
                                "type": base.MessageType.INFO})
            time0: float = time.perf_counter()

            potentialConnections: typing.List = solver.refine(refinementMethod, configParamRefinement)

            time1: float = time.perf_counter()
            computationTime += time1-time0
            self.progress.emit({"msg": "Found {} potential connections".format(len(potentialConnections)),
                                "type": base.MessageType.INFO})
            self.progress.emit({"msg": "> Done: {:.3f}s".format(time1-time0),
                                "type": base.MessageType.INFO})

            if not self._isRunning:
                self.__abort()
                return

            self.progress.emit({"msg": "====== Solving =======",
                                "type": base.MessageType.INFO})
            self.progress.emit({"msg": "Performing the {} solver method".format(solverMethod.value[0]),
                                "type": base.MessageType.INFO})
            time2: float = time.perf_counter()
        
            topologicalConstraints: typing.Set[typing.Tuple] = solver.solve(solverMethod, configParamSolver, potConnections=potentialConnections)

            time3: float = time.perf_counter()
            computationTime += time3-time2
            self.progress.emit({"msg": "FOUND {} TOPOLOGICAL CONSTRAINT(S)".format(len(topologicalConstraints)),
                                "type": base.MessageType.FOCUS})
            self.progress.emit({"msg": "> Done: {:.3f}s".format(time3-time2),
                                "type": base.MessageType.INFO})

            if not self._isRunning:
                self.__abort()
                return

            self.progress.emit({"msg": ">>> FINISHED",
                                "type": base.MessageType.INFO})

            self._isRunning = False
            self.finished.emit({"time": computationTime,
                                "constraints": topologicalConstraints})

        except Exception as e:
            self.progress.emit({"msg": ">>> ERROR\n{}\nERROR <<<".format(e),
                                "type": base.MessageType.ERROR})
            self.__abort()

    def __abort(self) -> None:
        self._isRunning = False
        self.progress.emit({"msg": ">>> ABORTED",
                            "type": base.MessageType.WARNING})
        self.finished.emit({})
