<template>
  <v-app-bar clipped-left dense app color="primary" dark class="d-print-none">
    <slot />
    <router-link to="/">
      <v-btn icon>
        <v-icon size="40"> {{ $globals.icons.primary }} </v-icon>
      </v-btn>
    </router-link>

    <div btn class="pl-2">
      <v-toolbar-title style="cursor: pointer" @click="$router.push('/')"> Mealie </v-toolbar-title>
    </div>

    {{ value }}

    <v-spacer></v-spacer>
    <!-- <v-tooltip bottom>
      <template #activator="{ on, attrs }">
        <v-btn icon class="mr-1" small v-bind="attrs" v-on="on">
          <v-icon v-text="isDark ? $globals.icons.weatherSunny : $globals.icons.weatherNight"> </v-icon>
        </v-btn>
      </template>
      <span>{{ isDark ? $t("settings.theme.switch-to-light-mode") : $t("settings.theme.switch-to-dark-mode") }}</span>
    </v-tooltip> -->
    <!-- <div v-if="false" style="width: 350px"></div>
    <div v-else>
      <v-btn icon @click="$refs.recipeSearch.open()">
        <v-icon> {{ $globals.icons.search }} </v-icon>
      </v-btn>
    </div> -->

    <!-- Navigation Menu -->
    <template v-if="menu">
      <v-btn v-if="$auth.loggedIn" text @click="$auth.logout()">
        <v-icon left>{{ $globals.icons.logout }}</v-icon>
        {{ $t("user.logout") }}
      </v-btn>
      <v-btn v-else text nuxt to="/user/login">
        <v-icon left>{{ $globals.icons.user }}</v-icon>
        {{ $t("user.login") }}
      </v-btn>
    </template>
  </v-app-bar>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: null,
    },
    menu: {
      type: Boolean,
      default: true,
    },
  },
});
</script>
    