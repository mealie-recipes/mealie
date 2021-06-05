# Usage

## Getting a Token

Currently Mealie doesn't support creating a long-live token. You can however get a token from the API. This example was pulled from the automatic API documentation provided by Mealie.

### Curl
```bash
curl -X 'POST' \
  'https://mealie-demo.hay-kot.dev/api/auth/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=changeme%40email.com&password=demo&scope=&client_id=&client_secret='

```

#### Response
```json
{
  "snackbar": {
    "text": "User Successfully Logged In",
    "type": "success"
  },
  "access_token": "your-long-token-string",
  "token_type": "bearer"
}
```

## Key Components

### Exploring Your Local API
On your local installation you can access interactive API documentation that provides `curl` examples and expected results. This allows you to easily test and interact with your API to identify places to include your own functionality. You can visit the documentation at `http://mealie.yourdomain.com/docs or see the example at the [Demo Site](https://mealie-demo.hay-kot.dev/docs)

### Recipe Extras
Recipes extras are a key feature of the Mealie API. They allow you to create custom json key/value pairs within a recipe to reference from 3rd part applications. You can use these keys to contain information to trigger automation or custom messages to relay to your desired device. 

For example you could add `{"message": "Remember to thaw the chicken"}` to a recipe and use the webhooks built into mealie to send that message payload to a destination to be processed.

![api-extras-gif](../assets/gifs/api-extras.gif)
