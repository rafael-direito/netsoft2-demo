*** Settings ***
Library        Peers.py

*** Test Cases ***
Testing if is possible to add and remove peers
    ${was_successful}=    Peers
    Should Be True      ${was_successful}