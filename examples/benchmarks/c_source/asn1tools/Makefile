all:
	gcc $(CFLAGS) $(OPT_SIZE) generated/*.c main.c -o main
	size main
	readelf -s -W main | sort -k3 -n
	valgrind $(MASSIF_FLAGS) --massif-out-file=main.massif ./main 1
	ms_print main.massif
	time ./main $(ENCODE_DECODE_ITERATIONS)
	gcc $(CFLAGS) $(OPT_SPEED) generated/*.c main.c -o main
	time ./main $(ENCODE_DECODE_ITERATIONS)

generate:
	rm -rf generated
	mkdir -p generated
	cd generated && \
	    env PYTHONPATH=../../../../.. \
	        python3 -m asn1tools generate_c_source \
	            --namespace uper --codec uper \
	            ../../my_protocol.asn

include ../common.mk
