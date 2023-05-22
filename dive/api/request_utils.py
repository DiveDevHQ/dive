import requests
import json


class ResponseResult:
    success = False
    error_description = None
    json_body = ""
    status_code = None


def get_request_with_bearer(url, access_token):
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    r = requests.get(url=url, headers=headers)
    return process_response(r)


def post_request_with_bearer(url, access_token, data):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-type': 'application/json;charset=UTF-8',
    }
    r = requests.post(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    return process_response(r)


def patch_request_with_bearer(url, access_token, data):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-type': 'application/json;charset=UTF-8',
    }
    r = requests.patch(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    return process_response(r)



def put_request_with_bearer(url, access_token, data):
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-type': 'application/json;charset=UTF-8',
    }
    r = requests.put(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    return process_response(r)


def delete_request_with_bearer(url, access_token):
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    r = requests.delete(url, headers=headers)
    return process_response(r)


def post_request_with_form(url, form_data):
    r = requests.post(url, data=form_data)
    return process_response(r)


# from pprint import pprint

def process_response(response):
    result = ResponseResult()
    result.status_code = response.status_code
    match response.status_code:
        case 200:
            result.error_description = ""
            result.success = True
        case 204:
            result.error_description = ""
            result.success = True
        case 207:
            result.error_description = ""
            result.success = True
        case 400:
            result.error_description = "Bad request"
        case 404:
            result.error_description = "Not found"
        case 405:
            result.error_description = "Method not allowed"
        case 406:
            result.error_description = "Not Acceptable"
        case 409:
            result.error_description = "Conflict"
        case 403:
            result.error_description = "Forbidden"
        case 500:
            result.error_description = "Internal error"
        case 521:
            result.error_description = "Web server is down"
        case 503:
            result.error_description = "Service temporarily unavailable"
        case 504:
            result.error_description = "Timeouts"
        case 502:
            result.error_description = "Timeouts"
        case 477:
            result.error_description = "Migration in Progress"
        case 525:
            result.error_description = "SSL issues"
        case 526:
            result.error_description = "SSL issues"
        case 401:
            result.error_description = "Unauthorized"
        case 429:
            result.error_description = "Too many requests"
        case 522:
            result.error_description = "Connection timed out"
        case 524:
            result.error_description = "Timeout"
        case 414:
            result.error_description = "URL too long"
        case _:
            result.success = True
            result.error_description = ""

    try:
        result.json_body = response.json()
    except ValueError:
        result.json_body = None

    return result
