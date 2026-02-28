#!/bin/python3
from query_pb2 import QueryResult
import chardet

def printBody(body):
    if len(body) >= 1 and len(body[0]) != 0:
        det = chardet.detect(body[0])
        s_data = body[0][:1500]
        encoding = det['encoding']
        print(encoding)
        if encoding:
            try:
                s_data = s_data.decode(det['encoding'], errors='replace')
            except:
                print("decode error")
        else:
            print("unknown encoding")
        print(repr(s_data))

def parseAtaResult(serialized_data):
    #print(serialized_data)
    result = QueryResult()
    result.ParseFromString(serialized_data)
    #print(f"    request_id: {result.access_log.request_id}")

    print(f"-------------------------request start----------------------------------------------")
    print(f"{result.access_log.request.raw_start_line}")
    print(f"{result.access_log.request.raw_headers}")
    printBody(result.access_log.request.raw_body)
    print(f"-------------------------request end----------------------------------------------")

    print(f"-------------------------response start----------------------------------------------")
    print(f"{result.access_log.response.raw_start_line}")
    print(f"{result.access_log.response.raw_headers}")
    printBody(result.access_log.response.raw_body)

    print(f"-------------------------response end----------------------------------------------")

