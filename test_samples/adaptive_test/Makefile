# Makefile for Testing RULE_BASED Architecture

CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -lm

SOURCES = main.c utils.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = myapp

.PHONY: all clean test install

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(OBJECTS) -o $(TARGET) $(LDFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET)

test: $(TARGET)
	./$(TARGET) --test

install: $(TARGET)
	install -m 755 $(TARGET) /usr/local/bin/

uninstall:
	rm -f /usr/local/bin/$(TARGET)
