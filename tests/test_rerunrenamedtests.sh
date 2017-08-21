#!/usr/bin/env bash

robot --prerunmodifier robottools.rename:one -o one hello.robot
robot --prerunmodifier robottools.rename:two -o two hello.robot
rebot --prerebotmodifier robottools.resetname one.xml
rebot --prerebotmodifier robottools.resetname two.xml
rebot -o both one.xml two.xml
rebot --prerebotmodifier robottools.resetname both.xml
robot --prerunmodifier robottools.rerunrenamedtests:both.xml hello.robot