# Frontend Configuration

## Environment Variables

### General

| Variables    |        Default         | Description                                                    |
| ------------ | :--------------------: | -------------------------------------------------------------- |
| ALLOW_SIGNUP |          true          | Allows anyone to sign-up for Mealie (should match backend env) |
| API_URL      | http://mealie-api:9000 | URL to proxy API requests                                      |

### Themeing
Setting the following environmental variables will change the theme of the frontend. Note that the themes are the same for all users. This is a break-change when migration from v0.x.x -> 1.x.x.

| Variables             | Default | Description                 |
| --------------------- | :-----: | --------------------------- |
| THEME_LIGHT_PRIMARY   | #E58325 | Light Theme Config Variable |
| THEME_LIGHT_ACCENT    | #007A99 | Light Theme Config Variable |
| THEME_LIGHT_SECONDARY | #973542 | Light Theme Config Variable |
| THEME_LIGHT_SUCCESS   | #43A047 | Light Theme Config Variable |
| THEME_LIGHT_INFO      | #1976D2 | Light Theme Config Variable |
| THEME_LIGHT_WARNING   | #FF6D00 | Light Theme Config Variable |
| THEME_LIGHT_ERROR     | #EF5350 | Light Theme Config Variable |
| DARK_LIGHT_PRIMARY    | #E58325 | Dark Theme Config Variable  |
| DARK_LIGHT_ACCENT     | #007A99 | Dark Theme Config Variable  |
| DARK_LIGHT_SECONDARY  | #973542 | Dark Theme Config Variable  |
| DARK_LIGHT_SUCCESS    | #43A047 | Dark Theme Config Variable  |
| DARK_LIGHT_INFO       | #1976D2 | Dark Theme Config Variable  |
| DARK_LIGHT_WARNING    | #FF6D00 | Dark Theme Config Variable  |
| DARK_LIGHT_ERROR      | #EF5350 | Dark Theme Config Variable  |
