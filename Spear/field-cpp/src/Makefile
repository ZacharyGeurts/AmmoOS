# SPDX-License-Identifier: MIT
# Spear — C++ and lower only. Scripts FORBIDDEN as product path.
CXX ?= g++
CXXFLAGS ?= -O2 -Wall -Wextra -std=c++17 -I.

CORE_SRCS = spear_main.cpp spear_ffat.cpp spear_elevate.cpp spear_field1.cpp spear_chip.cpp spear_fieldram.cpp spear_fieldmem.cpp spear_patdict.cpp
CORE_HDRS = spear_ffat.hpp spear_elevate.hpp spear_field1.hpp spear_chip.hpp spear_fieldram.hpp spear_fieldmem.hpp spear_patdict.hpp spear_sha256.hpp spear_common.hpp spear_plates.hpp

.PHONY: all clean install wartime field

all: spear spear-hard-dispose spear-copilot-monitor spear-wartime spear-kill-copilot spear-www spear-planet spear-export spear-fleet-link spear-i2-war spear-h7-panel spear-angel-seal spear-i2-server spear-field-surface field-calc field-menu field-terminal field-files field-audio field-net amouranthrtx spear-hostess7-boot

spear: $(CORE_SRCS) $(CORE_HDRS)
	$(CXX) $(CXXFLAGS) -o $@ $(CORE_SRCS) -lm

spear-hard-dispose: spear_hard_dispose.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_hard_dispose.cpp

spear-copilot-monitor: spear_copilot_monitor.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_copilot_monitor.cpp

spear-wartime: spear_wartime.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_wartime.cpp

spear-kill-copilot: spear_kill_copilot.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_kill_copilot.cpp

spear-www: spear_www.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_www.cpp

spear-planet: spear_planet.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_planet.cpp

spear-export: spear_export.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_export.cpp

spear-fleet-link: spear_fleet_link.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_fleet_link.cpp -lpthread

spear-i2-war: spear_i2_war.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_i2_war.cpp

spear-angel-seal: spear_angel_seal.cpp spear_chip.cpp spear_common.hpp spear_chip.hpp spear_sha256.hpp spear_plates.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_angel_seal.cpp spear_chip.cpp -lm

spear-i2-server: spear_i2_server.cpp spear_chip.cpp spear_common.hpp spear_chip.hpp spear_plates.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_i2_server.cpp spear_chip.cpp -lm

spear-h7-panel: spear_h7_panel.cpp spear_chip.cpp spear_common.hpp spear_chip.hpp spear_sha256.hpp spear_plates.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_h7_panel.cpp spear_chip.cpp -lm

spear-field-surface: spear_field_surface.cpp spear_common.hpp spear_field_surface.hpp spear_plates.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_field_surface.cpp

field-calc: field_calc.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_calc.cpp -lm

field-menu: field_menu.cpp spear_common.hpp spear_field_apps.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_menu.cpp

field-terminal: field_terminal.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_terminal.cpp

field-files: field_files.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_files.cpp

field-audio: field_audio.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_audio.cpp

field-net: field_net.cpp spear_common.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_net.cpp

amouranthrtx: field_amouranthrtx.cpp spear_common.hpp spear_field_surface.hpp spear_plates.hpp
	$(CXX) $(CXXFLAGS) -o $@ field_amouranthrtx.cpp

wartime: spear-wartime spear-kill-copilot spear-hard-dispose spear-www spear-planet spear-export spear-fleet-link spear-i2-war spear-h7-panel spear-angel-seal spear-i2-server spear-field-surface field-calc field-menu field-terminal field-files field-audio field-net amouranthrtx spear-hostess7-boot
field: all

install: all
	install -m 0755 spear-hard-dispose spear-copilot-monitor spear-wartime spear-kill-copilot spear-www spear-planet spear-export spear-fleet-link spear-i2-war spear-h7-panel spear-angel-seal spear-i2-server spear-field-surface \
	  field-calc field-menu field-terminal field-files field-audio field-net amouranthrtx spear-hostess7-boot \
	  $(HOME)/.local/bin/ 2>/dev/null || true
	install -m 0755 spear-hard-dispose spear-copilot-monitor spear-wartime spear-kill-copilot spear-www spear-planet spear-export spear-fleet-link spear-i2-war spear-h7-panel spear-angel-seal spear-i2-server spear-field-surface \
	  field-calc field-menu field-terminal field-files field-audio field-net amouranthrtx spear-hostess7-boot \
	  /home/zachary/Desktop/SG/Spear/overlay/usr/local/bin/ 2>/dev/null || true
	# native aliases — no bash wrappers (overwrite smart-guy scripts)
	ln -sfn $(HOME)/.local/bin/field-menu $(HOME)/.local/bin/spear-field-menu 2>/dev/null || true
	ln -sfn $(HOME)/.local/bin/amouranthrtx $(HOME)/.local/bin/field-amouranthrtx 2>/dev/null || true
	for a in field-ping field-telnet field-nc field-dig field-host field-nslookup field-internet-test field-curl field-network field-display field-traceroute; do \
	  ln -sfn $(HOME)/.local/bin/field-net $(HOME)/.local/bin/$$a 2>/dev/null || true; \
	  ln -sfn field-net /home/zachary/Desktop/SG/Spear/overlay/usr/local/bin/$$a 2>/dev/null || true; \
	done
	ln -sfn /home/zachary/Desktop/SG/Spear/overlay/usr/local/bin/field-menu \
	  /home/zachary/Desktop/SG/Spear/overlay/usr/local/bin/spear-field-menu 2>/dev/null || true
	-install -m 0755 spear /usr/local/bin/spear 2>/dev/null || true
	ln -sfn $(HOME)/.local/bin/spear-planet $(HOME)/.local/bin/spear-planet-live 2>/dev/null || true
	ln -sfn $(HOME)/.local/bin/spear-fleet-link $(HOME)/.local/bin/spear-rack-guard 2>/dev/null || true

clean:
	rm -f spear spear-hard-dispose spear-copilot-monitor spear-wartime spear-kill-copilot spear-www spear-planet spear-export spear-fleet-link spear-i2-war spear-h7-panel spear-angel-seal spear-i2-server spear-field-surface field-calc field-menu field-terminal field-files field-audio field-net amouranthrtx spear-hostess7-boot

spear-hostess7-boot: spear_hostess7_boot.cpp spear_common.hpp spear_field_apps.hpp spear_plates.hpp
	$(CXX) $(CXXFLAGS) -o $@ spear_hostess7_boot.cpp
