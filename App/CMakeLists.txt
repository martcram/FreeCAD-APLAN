include_directories(
    ${CMAKE_BINARY_DIR}
    ${CMAKE_SOURCE_DIR}/src
    ${CMAKE_BINARY_DIR}/src
    ${CMAKE_CURRENT_BINARY_DIR}
    ${Boost_INCLUDE_DIRS}
    ${OCC_INCLUDE_DIR}
    ${ZLIB_INCLUDE_DIR}
    ${PYTHON_INCLUDE_DIRS}
    ${XercesC_INCLUDE_DIRS}
)
link_directories(${OCC_LIBRARY_DIR})

set(Aplan_LIBS
    FreeCADApp
    Part
)

generate_from_xml(AplanAnalysisPy)
generate_from_xml(AplanCompoundGroupPy)

SET(Python_SRCS
    AplanAnalysisPy.xml
    AplanAnalysisPyImp.cpp
    AplanCompoundGroupPy.xml
    AplanCompoundGroupPyImp.cpp
)
SOURCE_GROUP("Python" FILES ${Python_SRCS})

SET(Mod_SRCS
    AppAplan.cpp
    AppAplanPy.cpp
    AplanTools.cpp
    AplanTools.hpp
    PreCompiled.cpp
    PreCompiled.hpp
)
SOURCE_GROUP("Module" FILES ${Mod_SRCS})

SET(AplanBase_SRCS
    AplanAnalysis.cpp
    AplanAnalysis.hpp
    AplanCompound.cpp
    AplanCompound.hpp
    AplanCompoundGroup.cpp
    AplanCompoundGroup.hpp
    AplanConnectionDetector.cpp
    AplanConnectionDetector.hpp
    AplanConstraintGroup.cpp
    AplanConstraintGroup.hpp
    AplanPartFilter.cpp
    AplanPartFilter.hpp
    AplanTopoConstraints.cpp
    AplanTopoConstraints.hpp
)
SOURCE_GROUP("Base types" FILES ${AplanBase_SRCS})

SET(Aplan_SRCS
    ${AplanBase_SRCS}
    ${Mod_SRCS}
    ${Python_SRCS}
)

add_library(Aplan SHARED ${Aplan_SRCS})
target_link_libraries(Aplan ${Aplan_LIBS})


SET_BIN_DIR(Aplan Aplan /Mod/Aplan)
SET_PYTHON_PREFIX_SUFFIX(Aplan)

INSTALL(TARGETS Aplan DESTINATION ${CMAKE_INSTALL_LIBDIR})
