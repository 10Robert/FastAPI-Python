from fastapi import params
import requests

params = {"ano": 2000}

r = requests.get("http://localhost:8000/books")
r_params = requests.get("http://localhost:8000/books/publish/", params=params)

#print(r.json())
print(r_params.json())

