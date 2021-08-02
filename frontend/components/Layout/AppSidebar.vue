<template>
  <v-navigation-drawer :value="value" clipped app width="200px">
    <!-- User Profile -->
    <template v-if="$auth.user">
      <v-list-item two-line to="/user/profile">
        <v-list-item-avatar color="accent" class="white--text">
          <v-img :src="require(`~/static/account.png`)" />
        </v-list-item-avatar>

        <v-list-item-content>
          <v-list-item-title> {{ $auth.user.fullName }}</v-list-item-title>
          <v-list-item-subtitle> {{ $auth.user.admin ? $t("user.admin") : $t("user.user") }}</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>
    </template>
    
    <!-- Primary Links -->
    <v-list nav dense>
      <v-list-item-group v-model="topSelected" color="primary">
        <v-list-item v-for="nav in topLink" :key="nav.title" link :to="nav.to">
          <v-list-item-icon>
            <v-icon>{{ nav.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ nav.title }}</v-list-item-title>
        </v-list-item>
      </v-list-item-group>
    </v-list>

    <!-- Secondary Links -->
    <template v-if="secondaryLinks">
      <v-divider></v-divider>
      <v-list nav dense>
        <v-list-item-group v-model="secondarySelected" color="primary">
          <v-list-item v-for="nav in secondaryLinks" :key="nav.title" link :to="nav.to">
            <v-list-item-icon>
              <v-icon>{{ nav.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ nav.title }}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </template>

    <!-- Bottom Navigation Links -->
    <template v-if="bottomLinks">
      <v-list class="fixedBottom" nav dense>
        <v-list-item-group v-model="bottomSelected" color="primary">
          <v-list-item
            v-for="nav in bottomLinks"
            :key="nav.title"
            link
            :to="nav.to || null"
            :href="nav.href || null"
            :target="nav.href ? '_blank' : null"
          >
            <v-list-item-icon>
              <v-icon>{{ nav.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ nav.title }}</v-list-item-title>
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </template>
  </v-navigation-drawer>
</template>
  
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { SidebarLinks } from "~/types/application-types";

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: null,
    },
    user: {
      type: Object,
      default: null,
    },
    topLink: {
      type: Array as () => SidebarLinks,
      required: true,
    },
    secondaryLinks: {
      type: Array as () => SidebarLinks,
      required: false,
      default: null,
    },
    bottomLinks: {
      type: Array as () => SidebarLinks,
      required: false,
      default: null,
    },
  },
  setup() {
    return {};
  },
  data() {
    return {
      topSelected: null,
      secondarySelected: null,
      bottomSelected: null,
    };
  },
});
</script>
  
<style>
.fixedBottom {
  position: fixed !important;
  bottom: 0 !important;
  width: 100%;
}

@media print {
  .no-print {
    display: none;
  }
}
</style>
