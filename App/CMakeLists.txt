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

SET(Mod_SRCS
    AppAplan.cpp
    AppAplanPy.cpp
    PreCompiled.cpp
    PreCompiled.hpp
)
SOURCE_GROUP("Module" FILES ${Mod_SRCS})

SET(AplanBase_SRCS
    AplanAnalysis.cpp
    AplanAnalysis.hpp
    AplanPartFilter.cpp
    AplanPartFilter.hpp
)
SOURCE_GROUP("Base types" FILES ${AplanBase_SRCS})

SET(Aplan_SRCS
    ${Mod_SRCS}
    ${AplanBase_SRCS}
)

add_library(Aplan SHARED ${Aplan_SRCS})
target_link_libraries(Aplan ${Aplan_LIBS})


SET_BIN_DIR(Aplan Aplan /Mod/Aplan)
SET_PYTHON_PREFIX_SUFFIX(Aplan)

INSTALL(TARGETS Aplan DESTINATION ${CMAKE_INSTALL_LIBDIR})
