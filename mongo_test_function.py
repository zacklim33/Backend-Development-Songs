import requests;



# To test exercise 4, creating a song
url = 'http://localhost:5000/song'
headers = {'Content-Type': 'application/json'}
data = {
    'id': 323,
    'lyrics': 'Integer tincidunt ante vel ipsum. Praesent blandit lacinia erat. Vestibulum sed magna at nunc commodo placerat.\n\nPraesent blandit. Nam nulla. Integer pede justo, lacinia eget, tincidunt eget, tempus vel, pede.',
    'title': 'in faucibus orci luctus et ultrices'
}

response = requests.post(url, headers=headers, json=data)
print (response.status_code)
print (response.json())