import urllib.request
import json

data = json.dumps({'message': 'I am hungry'}).encode('utf-8')
req = urllib.request.Request('http://127.0.0.1:8000/api/chatbot/', data=data, headers={'Content-Type': 'application/json'})
try:
    response = urllib.request.urlopen(req)
    print("SUCCESS:")
    print(response.read().decode('utf-8'))
except Exception as e:
    print("ERROR:")
    print(e)
