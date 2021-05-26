# Style Guide

!!! note
    Unifying styles across the application is an ongoing process, we are working on making the site more consistent.

## Button Guidelines

1. Buttons should follow the general color/icon scheme as outlined. 
2. All buttons should have an icon on the left side of the button and text on the right. 
3. Primary action buttons should be the default Vuetify styling. 
4. Primary action buttons should be right aligned
5. Secondary buttons should be `text` or `outlined`. Text is preferred
6. Other buttons should generally be "info" or "primary" color and can take any style type depending on context

### Button Colors and Icons

| Type        | Color               | Icon                                               |
| ----------- | :------------------ | :------------------------------------------------- |
| Default     | `info` or `primary` | None                                               |
| Create/New  | `success`           | `mdi-plus` or `$globals.icons.create`              |
| Update/Save | `success`           | `mdi-save-content` or `$globals.icons.save`        |
| Edit        | `info`              | `mdi-square-edit-outline` or `$globals.icons.edit` |

### Example
```html
<v-btn color="primary">
  <v-icon left> mdi-plus </v-icon>
  Primary Button
</v-btn>

```


