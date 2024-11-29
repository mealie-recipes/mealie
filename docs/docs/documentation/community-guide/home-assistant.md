!!! info
  This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

In a lot of ways, Home Assistant is why this project exists! Since Mealie has a robust API it makes it a great fit for interacting with Home Assistant and pulling information into your dashboard.

### Display Today's Meal in Lovelace

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
rest:
  - resource: "http://mealie:9000/api/households/mealplans/today"
    method: GET
    headers:
      Authorization: Bearer <<API_TOKEN>>
    scan_interval: 3600
    sensor:
      - name: Mealie todays meal
        value_template: "{{ value_json[0]['recipe']['name'] }}"
        force_update: true
        unique_id: mealie_todays_meal
      - name: Mealie todays meal ID
        value_template: "{{ value_json[0]['recipe']['id'] }}"
        force_update: true
        unique_id: mealie_todays_meal_id
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
