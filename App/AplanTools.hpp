/***************************************************************************
 *                                                                         *
 *   Copyright (c) 2022 Martijn Cramer <martijn.cramer@outlook.com>        *
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

#ifndef APLAN_TOOLS_HPP
#define APLAN_TOOLS_HPP

#include "PreCompiled.hpp"
#ifndef _PreComp_
#include <string>
#include <vector>
#endif

namespace Aplan
{
    class AplanAppExport Tools
    {
    public:
        /*!
        Splits a file path into its individual string components using '/' as the delimiter.
        */
        static std::vector<std::string> splitFilePath(const std::string &);
        /*!
        Merges individual string components into a file path '/' as the delimiter.
        */
        static std::string mergeIntoFilePath(const std::vector<std::string> &);
    };
} // namespace Aplan

#endif // APLAN_PARTFILTER_HPP