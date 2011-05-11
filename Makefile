# This Makefile git clones all of the software dependencies for this software
.PHONY: download

download: lib/oauth2 lib/Crypto

lib/oauth2:
	@echo "Downloading python-oauth2..."
	@git clone https://github.com/davidlehn/python-oauth2.git lib/oauth2  > /dev/null 2>&1

lib/Crypto:
	@echo "Downloading pycrypto..."
	@rm -rf /tmp/pycrypto.payswarm/
	@git clone https://github.com/dlitz/pycrypto.git /tmp/pycrypto.payswarm  > /dev/null 2>&1
	@echo "Building pycrypto..."
	@cd /tmp/pycrypto.payswarm && python setup.py build
	@echo "installing pycrypto to lib/Crypto..."
	@cd /tmp/pycrypto.payswarm && python setup.py install --home=/tmp/pycrypto.payswarm/tmp
	@mv /tmp/pycrypto.payswarm/tmp/lib/python/Crypto lib
	@rm -rf /tmp/pycrypto.payswarm/

