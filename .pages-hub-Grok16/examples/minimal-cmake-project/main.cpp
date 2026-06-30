// Grok16 smoke — C++20 compile test (examples/minimal-cmake-project)
#include <iostream>
#include <version>

int main() {
  std::cout << "Grok16 minimal example: __cplusplus=" << __cplusplus << '\n';
  return __cplusplus >= 202400L ? 0 : 1;
}