from flask import Response
import json
import datetime

def buildJson(result):
    return Response(response=json.dumps(result),
                    status=200,
                    mimetype="application/json")

def buildNoContentJson():
    return Response(response = '',
                    status=204,
                    mimetype="application/json")

def buildBadRequestJson(result):
    return Response(response=json.dumps(result),
                    status=400,
                    mimetype="application/json")

