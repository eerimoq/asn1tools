TESTS += test_oer.c
TESTS += test_uper.c

INC += files/c_source
SRC += files/c_source/oer.c
SRC += files/c_source/c_source-minus.c
SRC += files/c_source/uper.c
SRC += files/c_source/boolean_uper.c
SRC += files/c_source/octet_string_uper.c

CFLAGS += -Wall
CFLAGS += -Wextra
CFLAGS += -Wpedantic
CFLAGS += -Wsign-conversion
CFLAGS += -Wshadow
CFLAGS += -Werror

include test.mk
