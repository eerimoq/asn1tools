SHELL = /usr/bin/env bash

CFLAGS = \
	-Igenerated \
        -ffunction-sections \
        -fdata-sections \
	-Wl,--gc-sections

OPT_SIZE = -Os
OPT_SPEED = -O3

ENCODE_DECODE_ITERATIONS = 1000000

MASSIF_FLAGS = --tool=massif --time-unit=B --stacks=yes --detailed-freq=100
