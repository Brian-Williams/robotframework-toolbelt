*** Settings ***
Documentation     A robot file that is used as an acceptance test for the docker build.
Metadata          hello  world

*** Test Cases ***
Hello world test
    [Tags]    Hello-world
    log to console    \nHey World!

Fail me
    Fail