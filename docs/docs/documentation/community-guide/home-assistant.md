!!! info
  This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

In a lot of ways, Home Assistant is why this project exists! Since Mealie has a robust API it makes it a great fit for interacting with Home Assistant and pulling information into your dashboard.

## Display Today's Meal in Lovelace

You can use the Mealie API to get access to meal plans in Home Assistant like in the image below.

![api-extras-gif](../../assets/img/home-assistant-card.png)

Steps:

#### 1. Get your API Token

Create an API token from Mealie's User Settings page (https://hay-kot.github.io/mealie/documentation/users-groups/user-settings/#api-key-generation)

#### 2. Create Home Assistant Sensors

Create REST sensors in home assistant to get the details of today's meal.
We will create sensors to get the name and ID of the first meal in today's meal plan (note that this may not be what is wanted if there is more than one meal planned for the day). We need the ID as well as the name to be able to retrieve the image for the meal.

Make sure the url and port (`http://mealie:9000` ) matches your installation's address and _API_ port.

```yaml
- platform: rest
  resource: "http://mealie:9000/api/households/mealplans/today"
  method: GET
  name: Mealie todays meal
  headers:
    Authorization: Bearer <<API_TOKEN>>
  value_template: "{{ value_json[0].recipe.name }}"
  force_update: true
  scan_interval: 30
```

```yaml
- platform: rest
  resource: "http://mealie:9000/api/households/mealplans/today"
  method: GET
  name: Mealie todays meal ID
  headers:
    Authorization: Bearer <<API_TOKEN>>
  value_template: "{{ value_json[0].recipe.id }}"
  force_update: true
  scan_interval: 30
```

#### 3. Create a Camera Entity

We will create a camera entity to display the image of today's meal in Lovelace.

In Home Assistant's `Integrations` page, create a new `generic camera` entity.

In the still image url field put in:
`http://mealie:9000/api/media/recipes/{{states('sensor.mealie_todays_meal_id')}}/images/min-original.webp`

Under the entity page for the new camera, rename it.
e.g. `camera.mealie_todays_meal_image`

#### 4. Create a Lovelace Card

Create a picture entity card and set the entity to `mealie_todays_meal` and the camera entity to `camera.mealie_todays_meal_image` or set in the yaml directly.

```yaml
show_state: true
show_name: true
camera_view: auto
type: picture-entity
entity: sensor.mealie_todays_meal
name: Dinner Tonight
camera_image: camera.mealie_todays_meal_image
card_mod:
  style: |
    ha-card {
    max-height: 300px !important;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    }
```

!!! tip
Due to how Home Assistant works with images, I had to include the additional styling to get the images to not appear distorted. This requires an [additional installation](https://github.com/thomasloven/lovelace-card-mod) from HACS.

## Extended Example

![api-extras-gif](../../assets/img/home-assistant-cards.png)

Steps:

#### 1. Repeat Step 1 Above to get Your API Token

#### 2. Create Home Assistant Sensors

Create REST sensors in home assistant

Make sure the url and port (`http://mealie:9000` ) matches your installation's address and _API_ port. Configure the page (`1`), perPage (`5`), and orderDirection (`asc`) as desired. This example will return 1 page with 5 meals per page in ascending order starting today to exclude yesterday's meals. 

```yaml
rest:
  - resource_template: http://mealie:9000/api/groups/mealplans?start_date={{ now().strftime('%Y-%m-%d') }}&page=1&perPage=5&orderBy=date&orderDirection=asc
    method: GET <<API_TOKEN>>
    headers:
      Authorization: Bearer 
    scan_interval: 30
    
    sensor:
      - name: "Mealie 1 name"
        value_template: "{{ value_json['items'][0].recipe.name | default }}"
      - name: "Mealie 1 id"
        value_template: "{{ value_json['items'][0].recipe.id | default }}"
      - name: "Mealie 1 date"
        value_template: "{{ value_json['items'][0].date | default }}"
      - name: "Mealie 1 type"
        value_template: "{{ value_json['items'][0].entryType | default }}"
      - name: "Mealie 1 day"
        value_template: >-
            {% if now().strftime('%Y-%m-%d') == value_json['items'][0].date %}
            Today
            {% elif ((now().date() + timedelta(days=1)) | as_datetime) == (value_json['items'][0].date | as_datetime) %}
            Tomorrow
            {% else %}
            {{ (value_json['items'][0].date|as_datetime).strftime('%A') | default }}
            {% endif %}
            
      - name: "Mealie 2 name"
        value_template: "{{ value_json['items'][1].recipe.name | default }}"
      - name: "Mealie 2 id"
        value_template: "{{ value_json['items'][1].recipe.id | default }}"
      - name: "Mealie 2 date"
        value_template: "{{ value_json['items'][1].date | default }}"
      - name: "Mealie 2 type"
        value_template: "{{ value_json['items'][1].entryType | default }}"
      - name: "Mealie 2 day"
        value_template: >-
            {% if now().strftime('%Y-%m-%d') == value_json['items'][1].date %}
            Today
            {% elif ((now().date() + timedelta(days=1)) | as_datetime) == (value_json['items'][1].date | as_datetime) %}
            Tomorrow
            {% else %}
            {{ (value_json['items'][1].date|as_datetime).strftime('%A') | default }}
            {% endif %}

      etc...
```

#### 3. Repeat Step 3 Above to Create a Camera Entity for Each Meal

#### 4. Create Lovelace Cards for Each Meal

```yaml
type: conditional
conditions:
  - condition: state
    entity: sensor.mealie_1_name
    state_not: unknown
card:
  type: custom:config-template-card
  variables:
    DAY: states['sensor.mealie_1_day'].state
    TYPE: states['sensor.mealie_1_type'].state
    ID: states['sensor.mealie_1_id'].state
  entities:
    - sensor.mealie_1_day
    - sensor.mealie_1_type
    - sensor.mealie_1_id
  card:
    type: picture-entity
    show_state: true
    show_name: true
    camera_view: auto
    entity: sensor.mealie_1_name
    name: ${TYPE[0].toUpperCase() + TYPE.slice(1) + " " + DAY}
    camera_image: camera.mealie_1_image
    aspect_ratio: 16x9
    tap_action:
      action: url
      url_path: ${"https://mealie:9000/g/home/r/" + ID}
```

!!! tip
The [config-template-card]([https://github.com/iantrich/config-template-card]) from HACS allows us to dynamically use our sesnor values in the `picture-entity` card. 
