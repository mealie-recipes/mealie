# Usage

## Key Components
### Recipe Extras
Recipes extras are a key feature of the Mealie API. They allow you to create custom json key/value pairs within a recipe to reference from 3rd part applications. You can use these keys to contain information to trigger automation or custom messages to relay to your desired device. 

For example you could add `{"message": "Remember to thaw the chicken"}` to a recipe and use the webhooks built into mealie to send that message payload to a destination to be processed.

![api-extras-gif](../assets/gifs/api-extras.gif)


## Examples
### Bulk import
Recipes can be imported in bulk from a file containing a list of URLs. This can be done using the following bash or python scripts with the `list` file containing one URL per line.

#### Bash
```bash
#!/bin/bash

function authentification () {
  auth=$(curl -X 'POST' \
    "$3/api/auth/token" \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username='$1'&password='$2'&scope=&client_id=&client_secret=')

    echo $auth |  sed -e 's/.*token":"\(.*\)",.*/\1/'
}

function import_from_file () {
  while IFS= read -r line
  do
    echo $line
    curl -X 'POST' \
      "$3/api/recipes/create-url" \
      -H "Authorization: Bearer $2" \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{"url": "'$line'" }'
    echo
  done < "$1"
}

input="list"
mail="changeme@email.com"
password="MyPassword"
mealie_url=http://localhost:9000


token=$(authentification $mail $password $mealie_url)
import_from_file $input $token $mealie_url

```

#### Python
```python
import requests
import re

def authentification(mail, password, mealie_url):
  headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
  }
  data = {
    'grant_type': '',
    'username': mail,
    'password': password,
    'scope': '',
    'client_id': '',
    'client_secret': ''
  }
  auth = requests.post(mealie_url + "/api/auth/token", headers=headers, data=data)
  token = re.sub(r'.*token":"(.*)",.*', r'\1', auth.text)
  return token

def import_from_file(input_file, token, mealie_url):
  with open(input_file) as fp:
    for l in fp:
      line = re.sub(r'(.*)\n', r'\1', l)
      print(line)
      headers = {
        'Authorization': "Bearer " + token,
        'accept': 'application/json',
        'Content-Type': 'application/json'
      }
      data = {
        'url': line
      }
      response = requests.post(mealie_url + "/api/recipes/create-url", headers=headers, json=data)
      print(response.text)

input_file="list"
mail="changeme@email.com"
password="MyPassword"
mealie_url="http://localhost:9000"


token = authentification(mail, password, mealie_url)
import_from_file(input_file, token, mealie_url)
```

Have Ideas? Submit a PR!
