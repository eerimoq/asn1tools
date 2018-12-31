CFLAGS = \
	-Igenerated \
	-Os \
        -ffunction-sections \
        -fdata-sections \
	-Wl,--gc-sections

MASSIF_FLAGS = --tool=massif --time-unit=B --stacks=yes --detailed-freq=100
