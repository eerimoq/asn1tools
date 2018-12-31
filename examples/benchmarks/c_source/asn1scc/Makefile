all:
	gcc $(CFLAGS) generated/*.c main.c -o main
	size main
	readelf -s -W main | sort -k3 -n
	valgrind $(MASSIF_FLAGS) --massif-out-file=main.massif ./main
	ms_print main.massif

# Execute in asn1scc docker image.
generate:
	rm -rf generated
	mkdir -p generated
	cd generated && \
	    mono /usr/local/share/asn1scc/asn1.exe -c -uPER ../my_protocol.asn

include ../common.mk
