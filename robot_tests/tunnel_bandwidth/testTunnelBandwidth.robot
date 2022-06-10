*** Settings ***
Library        TunnelBandwidth.py

*** Test Cases ***
Testing if the tunnel bandwidth is >= 100 mbits/sec
    ${mbits_sec}=    TunnelBandwidth
    IF     '${mbits_sec}' != '-1'
    Should Be True    ${mbits_sec} >= 100
    ELSE
    FAIL    \nImpossible to compute bandwidth
    END