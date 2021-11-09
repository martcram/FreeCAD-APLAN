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

#ifndef APLANGUI_PRECOMPILED_HPP
#define APLANGUI_PRECOMPILED_HPP

#include <FCConfig.h>

// Importing of App classes
#ifdef FC_OS_WIN32
#define AplanAppExport __declspec(dllimport)
#define AplanExport __declspec(dllimport)
#define AplanGuiExport __declspec(dllexport)
#else // for Linux
#define AplanAppExport
#define AplanExport
#define AplanGuiExport
#endif

#ifdef _MSC_VER
#pragma warning(disable : 4005)
#pragma warning(disable : 4290)
#endif

#ifdef _PreComp_

// Python
#include <Python.h>

// standard
#include <iostream>
#include <assert.h>
#include <cmath>

#include <math.h>

// STL
#include <vector>
#include <map>
#include <string>
#include <list>
#include <set>
#include <algorithm>
#include <stack>
#include <queue>
#include <bitset>
#include <sstream>

// boost
#include <boost/bind/bind.hpp>
#include <boost/lexical_cast.hpp>

#ifdef FC_OS_WIN32
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#endif

// OCC
#include <Standard_math.hxx>
#include <Precision.hxx>
#include <TopoDS.hxx>
#include <BRepAdaptor_Surface.hxx>
#include <Geom_Plane.hxx>
#include <gp_Pln.hxx>
#include <gp_Ax1.hxx>
#include <BRepAdaptor_Curve.hxx>
#include <Geom_Line.hxx>
#include <gp_Lin.hxx>
#include <Standard_PrimitiveTypes.hxx>
#include <TopoDS_Shape.hxx>

// Qt Toolkit
#ifndef __Qt4All__
#include <Gui/Qt4All.h>
#endif

#endif //_PreComp_

#endif // APLANGUI_PRECOMPILED_H
