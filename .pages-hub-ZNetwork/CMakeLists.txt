cmake_minimum_required(VERSION 3.16)
project(ZNetwork VERSION 2.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(ZNETWORK_BUILD_TESTS "Build ZNetwork unit tests" OFF)

set(ZNETWORK_CORE_SOURCES
  src/platform.cpp
  src/mode.cpp
  src/connection_snapshot.cpp
  src/slide_in.cpp
  src/field_security.cpp
  src/ddos_shield.cpp
  src/negotiation_guard.cpp
  src/confirm_dialog.cpp
)

string(TOLOWER "${CMAKE_CXX_COMPILER}" ZNETWORK_CXX_COMPILER_LOWER)
set(ZNETWORK_TARGET_WIN OFF)
if(WIN32 OR ZNETWORK_CXX_COMPILER_LOWER MATCHES "mingw")
  set(ZNETWORK_TARGET_WIN ON)
endif()

if(ZNETWORK_TARGET_WIN)
  list(APPEND ZNETWORK_CORE_SOURCES
    src/connection_snapshot_win.cpp
    src/native_backend_win.cpp)
elseif(APPLE)
  list(APPEND ZNETWORK_CORE_SOURCES
    src/connection_snapshot_darwin.cpp
    src/native_backend_darwin.cpp)
elseif(UNIX)
  list(APPEND ZNETWORK_CORE_SOURCES
    src/connection_snapshot_linux.cpp
    src/native_backend_linux.cpp)
endif()

add_library(znetwork_core STATIC ${ZNETWORK_CORE_SOURCES})

target_include_directories(znetwork_core PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)

if(ZNETWORK_TARGET_WIN)
  target_compile_definitions(znetwork_core PUBLIC ZNETWORK_WIN=1)
  target_link_libraries(znetwork_core PUBLIC ws2_32 iphlpapi)
elseif(APPLE)
  target_compile_definitions(znetwork_core PUBLIC ZNETWORK_DARWIN=1)
elseif(UNIX)
  target_compile_definitions(znetwork_core PUBLIC ZNETWORK_LINUX=1)
endif()

add_executable(znetwork src/main.cpp)
target_compile_definitions(znetwork PRIVATE ZNETWORK_VERSION="${PROJECT_VERSION}-review")
target_link_libraries(znetwork PRIVATE znetwork_core)

install(TARGETS znetwork RUNTIME DESTINATION bin)
install(DIRECTORY include/znetwork DESTINATION include)
install(FILES data/znetwork-manifest.json data/review-checklist.json DESTINATION share/znetwork)