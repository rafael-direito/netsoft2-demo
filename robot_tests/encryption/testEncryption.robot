*** Settings ***
Library        Encryption.py

*** Test Cases ***
Testing if the tunnel communication is encrypted
    ${is_encrypted}=    Encryption
    Should Be True      ${is_encrypted}