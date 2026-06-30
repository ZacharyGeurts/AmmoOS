cmake_minimum_required(VERSION 3.16)
project(grok16_minimal_smoke CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(grok16_smoke main.cpp)
if(COMMAND g16_ironclad_sanity_meld)
  g16_ironclad_sanity_meld(grok16_smoke)
endif()