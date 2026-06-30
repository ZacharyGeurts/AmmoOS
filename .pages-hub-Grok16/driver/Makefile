# Build Grok16 unified driver (host gcc)
CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11
PREFIX ?= ..
TARGET = g16-unified

.PHONY: all clean install

all: $(TARGET)

$(TARGET): g16-unified.c
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm -f $(TARGET)

install: $(TARGET)
	install -d $(PREFIX)/bin $(PREFIX)/libexec/grok16
	install -m 755 $(TARGET) $(PREFIX)/bin/g16
	ln -sf g16 $(PREFIX)/bin/g++16