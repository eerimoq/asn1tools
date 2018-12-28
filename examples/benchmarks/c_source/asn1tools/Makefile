all:

generate:
	rm -rf generated
	mkdir -p generated
	cd generated && \
	    env PYTHONPATH=../../../../.. \
	        python3 -m asn1tools generate_c_source \
	            --namespace uper --codec uper \
	            ../../my_protocol.asn
