cmake_minimum_required(VERSION 3.16)
project(grok16_field_canvas CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(EXISTS "${CMAKE_CURRENT_LIST_DIR}/../../cmake/grok16-profile-field.cmake")
  include("${CMAKE_CURRENT_LIST_DIR}/../../cmake/grok16-profile-field.cmake")
endif()

add_executable(field_canvas_kernel field_dispatch.cpp)
if(COMMAND g16_ironclad_sanity_meld)
  g16_ironclad_sanity_meld(field_canvas_kernel)
endif()