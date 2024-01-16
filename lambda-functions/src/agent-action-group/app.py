def lambda_handler(event, context):
    response_body = {
        'application/json': {
            'body': [
              {
                "reportId": "01REJ3REQFJGHGDOFIL5DYH3O5JN6I47LD",
                "fileName": "58_202308.pdf",
                "webUrl": "https://stonecastle.sharepoint.com/sites/FinancialAuditSupport/Shared%20Documents/Test-FirstFactory/2023/2023_08/Bank%20Statements/58_202308.pdf"
              },
              {
                "reportId": "01REJ3REQVQCPDDHJZ4ZEKKGDOZTHG37TI",
                "fileName": "94_202307.pdf",
                "webUrl": "https://stonecastle.sharepoint.com/sites/FinancialAuditSupport/Shared%20Documents/Test-FirstFactory/2023/2023_07/Bank%20Statements/94_202307.pdf"
              },
              {
                "reportId": "01REJ3RERFPIYOTRPE2ZGITXQZKEH352ME",
                "fileName": "1210_202305.pdf",
                "webUrl": "https://stonecastle.sharepoint.com/sites/FinancialAuditSupport/Shared%20Documents/Test-FirstFactory/2023/2023_05/Bank%20Statements/1210_202305.pdf"
              }
            ]
        }
    }

    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        'httpMethod': event['httpMethod'],
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    session_attributes = event['sessionAttributes']
    prompt_session_attributes = event['promptSessionAttributes']

    api_response = {
        'messageVersion': '1.0',
        'response': action_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }

    return api_response
