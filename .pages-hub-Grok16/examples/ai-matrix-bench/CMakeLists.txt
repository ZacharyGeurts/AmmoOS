cmake_minimum_required(VERSION 3.16)
project(grok16_ai_matrix_bench CXX)

set(CMAKE_CXX_STANDARD 26)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(EXISTS "${CMAKE_CURRENT_LIST_DIR}/../../cmake/grok16-profile-ai.cmake")
  include("${CMAKE_CURRENT_LIST_DIR}/../../cmake/grok16-profile-ai.cmake")
endif()

add_executable(grok16_matrix_bench matrix_bench.cpp)
if(COMMAND g16_ironclad_sanity_meld)
  g16_ironclad_sanity_meld(grok16_matrix_bench)
endif()