*** Settings ***
Documentation     A robot file that is used as an acceptance test for the docker build.
Metadata          hello  world

*** Test Cases ***
Hello world test 2
    [Tags]    Hello-world
    log to console    \nHey World!

Fail me 2
    Fail