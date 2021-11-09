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

#ifndef APLAN_PRECOMPILED_HPP
#define APLAN_PRECOMPILED_HPP

#include <FCConfig.h>

// Exporting of App classes
#ifdef FC_OS_WIN32
#define AplanAppExport __declspec(dllexport)
#define AplanExport __declspec(dllexport)
#define BaseExport     __declspec(dllimport)
#define PartExport __declspec(dllimport)
#else // for Linux
#define AplanAppExport
#define AplanExport
#define BaseExport
#define PartExport
#endif

#ifdef _MSC_VER
#pragma warning(disable : 4290)
#pragma warning(disable : 4275)
#endif

#ifdef _PreComp_

// standard
#include <iostream>
#include <sstream>
#include <stdio.h>
#include <assert.h>
#include <string>
#include <map>
#include <vector>
#include <set>
#include <bitset>
#include <cstdlib>
#include <memory>
#include <cmath>

#include <math.h>

#include <algorithm>
#include <stdexcept>
// Python
#include <Python.h>

// Opencascade
#include <gp_Dir.hxx>
#include <gp_Lin.hxx>
#include <gp_Pln.hxx>
#include <gp_Pnt.hxx>
#include <gp_Vec.hxx>
#include <Adaptor3d_IsoCurve.hxx>
#include <Bnd_Box.hxx>
#include <BRep_Tool.hxx>
#include <BRepAdaptor_Curve.hxx>
#include <BRepAdaptor_HSurface.hxx>
#include <BRepAdaptor_Surface.hxx>
#include <BRepBndLib.hxx>
#include <BRepBuilderAPI_Copy.hxx>
#include <BRepBuilderAPI_MakeVertex.hxx>
#include <BRepClass_FaceClassifier.hxx>
#include <BRepExtrema_DistShapeShape.hxx>
#include <BRepGProp.hxx>
#include <BRepGProp_Face.hxx>
#include <BRepTools.hxx>
#include <ElCLib.hxx>
#include <ElSLib.hxx>
#include <GCPnts_AbscissaPoint.hxx>
#include <Geom_BezierCurve.hxx>
#include <Geom_BezierSurface.hxx>
#include <Geom_BSplineCurve.hxx>
#include <Geom_BSplineSurface.hxx>
#include <Geom_Line.hxx>
#include <Geom_Plane.hxx>
#include <GeomAPI_IntCS.hxx>
#include <GeomAPI_ProjectPointOnSurf.hxx>
#include <GProp_GProps.hxx>
#include <Precision.hxx>
#include <Standard_Real.hxx>
#include <ShapeAnalysis_ShapeTolerance.hxx>
#include <TColgp_Array2OfPnt.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Solid.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Vertex.hxx>

#endif // _PreComp_

#endif // APLAN_PRECOMPILED_HPP
