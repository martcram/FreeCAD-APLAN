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

#include "PreCompiled.hpp"
#ifndef _PreComp_
#include <sstream>
#include <string>
#include <vector>
#endif

#include <Mod/Aplan/App/AplanTools.hpp>

// Along the lines of https://stackoverflow.com/questions/9435385/split-a-string-using-c11
std::vector<std::string> Aplan::Tools::splitFilePath(const std::string &filePath)
{
    std::istringstream ss{filePath};
    std::string component{};
    std::vector<std::string> components{};
    while (std::getline(ss, component, '/'))
    {
        components.push_back(std::move(component));
    }
    if (components.at(0).empty())
    {
        components.erase(components.begin());
    }
    return components;
}

std::string Aplan::Tools::mergeIntoFilePath(const std::vector<std::string> &components)
{
    char delimiter{};
#ifdef FC_OS_WINDOWS
    delimiter = '\\';
#else // for Linux
    delimiter = '/';
#endif

    std::ostringstream ss{};
    for (const std::string &component : components)
    {
        ss << delimiter << component;
    }
    return ss.str();
}