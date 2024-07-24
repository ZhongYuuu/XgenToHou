cmake_minimum_required(VERSION 3.10)

# 设置项目名
project(XgenToHou)
set(XGEN_DIR ${CMAKE_CURRENT_SOURCE_DIR}/xgen)

# 设置C++标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# 添加包含目录
include_directories(${XGEN_DIR}/include)

# 添加库目录
link_directories(${XGEN_DIR}/lib)

# 查找所有源文件
file(GLOB_RECURSE SOURCES "src/*.cpp")

# 设置可执行文件
set(SOURCES main.cpp)
add_executable(XgenToHou ${SOURCES})


target_link_libraries(XgenToHou optimized ${XGEN_DIR}/lib/AdskXGen.lib 
                                optimized ${XGEN_DIR}/lib/AdskSeExpr.lib 
                                optimized ${XGEN_DIR}/lib/AdskXpd.lib)


# 查找所有DLL文件
file(GLOB DLL_FILES ${XGEN_DIR}/bin/*.dll)

# 复制DLL文件到可执行文件目录
foreach(DLL ${DLL_FILES})
    add_custom_command(TARGET XgenToHou POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
        ${DLL} $<TARGET_FILE_DIR:XgenToHou>)
endforeach()
