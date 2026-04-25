*** Settings ***
Library    SeleniumLibrary
Library    helper.py
Suite Teardown    Close All Browsers


*** Variables ***
${REPORT_FILE}        file:///C:/Users/NataliyaShabat/dqe-automation/Robot Framework/report.html
${PARQUET_FOLDER_REAL}     C:/Users/NataliyaShabat/dqe-automation/Robot Framework/parquet_data/facility_type_avg_time_spent_per_visit_date
${PARQUET_FOLDER_TEST}     C:/Users/NataliyaShabat/dqe-automation/Robot Framework/test_dataset.parquet
${FILTER_DATE}        2026-03-17


*** Test Cases ***
Validate HTML Report Against REAL Parquet Dataset
    Open Report In Browser
    ${table}=    Get Report Table Element

    ${html_df}=    Extract Html Table To Df    ${table}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet Dataset    ${PARQUET_FOLDER_REAL}    ${FILTER_DATE}

    Log TO Console      HTML DF: ${html_df}
    Log TO Console      PARQUET DF: ${parquet_df}

    ${result}    ${diff}=    Compare Dataframes    ${html_df}    ${parquet_df}

    Log TO Console      RESULT: ${result}
    Log TO Console      DIFF:${diff}

    Should Be True    ${result}

*** Test Cases ***
Validate HTML Report Against TEST Parquet Dataset
    Open Report In Browser
    ${table}=    Get Report Table Element

    ${html_df}=    Extract Html Table To Df    ${table}    ${FILTER_DATE}
    ${parquet_df}=    Read Parquet Dataset    ${PARQUET_FOLDER_TEST}    ${FILTER_DATE}

    Log TO Console      HTML DF: ${html_df}
    Log TO Console      PARQUET DF: ${parquet_df}

    ${result}    ${diff}=    Compare Dataframes    ${html_df}    ${parquet_df}

    Log TO Console      RESULT: ${result}
    Log TO Console      DIFF:${diff}

    Should Be True    ${result}


*** Keywords ***
Open Report In Browser
    Open Browser    ${REPORT_FILE}    chrome
    Log Source
    Maximize Browser Window
    Wait Until Page Contains Element     xpath=//body     20s
    Wait Until Keyword Succeeds     20s     2s  Page Should Contain Element   xpath=//*[name()='g' and contains(@class,'table')]
    Log   Report page loaded successfully
   

Get Report Table Element
    ${table}=    Get WebElement    xpath=//*[name()='g' and contains(@class,'table')]
    RETURN    ${table}