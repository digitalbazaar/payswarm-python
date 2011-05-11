# This Makefile git clones all of the software dependencies for this software
.PHONY: download

download: lib/oauth2 lib/Crypto

lib/oauth2:
	@echo "Downloading python-oauth2 to lib/oauth2..."
	@git clone https://github.com/davidlehn/python-oauth2.git /tmp/oauth2.payswarm > /dev/null 2>&1
	@mv /tmp/oauth2.payswarm/oauth2 lib
	@rm -rf /tmp/oauth2.payswarm

lib/Crypto:
	@echo "Downloading pycrypto..."
	@rm -rf /tmp/pycrypto.payswarm/
	@git clone https://github.com/dlitz/pycrypto.git /tmp/pycrypto.payswarm  > /dev/null 2>&1
	@echo "Building pycrypto..."
	@cd /tmp/pycrypto.payswarm && python setup.py build > /dev/null 2>&1
	@echo "Installing pycrypto to lib/Crypto..."
	@cd /tmp/pycrypto.payswarm && python setup.py install --home=/tmp/pycrypto.payswarm/tmp > /dev/null 2>&1
	@mv /tmp/pycrypto.payswarm/tmp/lib/python/Crypto lib
	@rm -rf /tmp/pycrypto.payswarm

