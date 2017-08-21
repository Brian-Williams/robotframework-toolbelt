#!/usr/bin/env bash

robot --prerunmodifier robottools.rename:one -o one hello.robot
robot --prerunmodifier robottools.rename:two -o two hello.robot
# make sure names can be reset
rebot --prerebotmodifier robottools.resetname one.xml
# make sure chained naming can be reset
rebot --prerebotmodifier robottools.resetname -o two_mod two.xml
rebot --prerebotmodifier robottools.resetname -o two_mod two.xml
rebot --prerebotmodifier robottools.resetname two_mod.xml

rebot -o both one.xml two.xml
rebot --prerebotmodifier robottools.resetname both.xml
robot --prerunmodifier robottools.rerunrenamedtests:both.xml hello.robot
