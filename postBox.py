import requests

def post_box():
   payload = { 
            "name": "Peter Lustigs Waage",
            "location": {
               "lat": 51.399206,
               "lon": 9.688879
               },
            "mail": {"adresses": ["xxx.xxx@countyourbirds.org"]}
            }
            
   r = requests.post("https://wiediversistmeingarten.org/api/station", json=payload)
   print(r.content)

post_box()
