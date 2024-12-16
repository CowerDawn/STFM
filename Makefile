CC = gcc
CFLAGS = -Wall -Wextra -std=c99
TARGET = stfm
PYTHON = python3

all: $(TARGET) run_sgfm

$(TARGET): STFM.c
	$(CC) $(CFLAGS) -o $(TARGET) STFM.c

run_sgfm: SGFM.py
	$(PYTHON) SGFM.py

clean:
	rm -f $(TARGET)
