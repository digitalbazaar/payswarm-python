# This Makefile git clones all of the software dependencies for this software
.PHONY: download

download: lib/oauth2

lib/oauth2:
	@echo "Downloading python-oauth2 to lib/oauth2..."
	@git clone https://github.com/davidlehn/python-oauth2.git /tmp/oauth2.payswarm > /dev/null 2>&1
	@mv /tmp/oauth2.payswarm/oauth2 lib
	@rm -rf /tmp/oauth2.payswarm

