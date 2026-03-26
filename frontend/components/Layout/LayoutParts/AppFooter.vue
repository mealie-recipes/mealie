<template>
  <v-footer
    color="primary"
    padless
    app
  >
    <v-row
      justify="center"
      align="center"
      dense
      no-gutters
    >
      <v-col
        class="py-2 text-center white--text"
        cols="12"
      >
        <v-btn
          color="white"
          icon
          href="https://github.com/mealie-recipes/mealie"
          target="_blank"
        >
          <v-icon>
            {{ $globals.icons.github }}
          </v-icon>
        </v-btn>
        {{ new Date().getFullYear() }} — <strong> Mealie </strong>
      </v-col>
    </v-row>
  </v-footer>
</template>
