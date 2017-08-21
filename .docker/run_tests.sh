#!/usr/bin/env bash

# add test dependancies to the host (most likely a container)
pip install -e /repo[test]
cd /repo && pytest
