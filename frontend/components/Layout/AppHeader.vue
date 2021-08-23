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
    <v-menu
      v-if="menu"
      transition="slide-x-transition"
      bottom
      right
      offset-y
      offset-overflow
      open-on-hover
      close-delay="200"
    >
      <template #activator="{ on, attrs }">
        <v-btn v-bind="attrs" icon v-on="on">
          <v-icon>{{ $globals.icons.user }}</v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item-group v-model="itemSelected" color="primary">
          <v-list-item
            v-for="(item, i) in filteredItems"
            :key="i"
            link
            :to="item.nav ? item.nav : null"
            @click="item.logout ? $auth.logout() : null"
          >
            <v-list-item-icon>
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>
                {{ item.title }}
              </v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-menu>
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
  setup() {
    return {};
  },
  data() {
    return {
      itemSelected: null,
      items: [
        {
          icon: this.$globals.icons.user,
          title: this.$t("user.login"),
          restricted: false,
          nav: "/user/login",
        },
        {
          icon: this.$globals.icons.logout,
          title: this.$t("user.logout"),
          restricted: true,
          logout: true,
        },
        {
          icon: this.$globals.icons.cog,
          title: this.$t("general.settings"),
          nav: "/user/profile",
          restricted: true,
        },
      ],
    };
  },
  computed: {
    filteredItems(): Array<any> {
      if (this.loggedIn) {
        return this.items.filter((x) => x.restricted === true);
      } else {
        return this.items.filter((x) => x.restricted === false);
      }
    },
    loggedIn(): Boolean {
      return this.$auth.loggedIn;
    },
  },
});
</script>
    