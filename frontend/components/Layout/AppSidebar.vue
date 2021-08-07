<template>
  <v-navigation-drawer :value="value" clipped app>
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
        <v-list-item v-for="nav in topLink" :key="nav.title" exact link :to="nav.to">
          <v-list-item-icon>
            <v-icon>{{ nav.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ nav.title }}</v-list-item-title>
        </v-list-item>
      </v-list-item-group>
    </v-list>

    <!-- Secondary Links -->
    <template v-if="secondaryLinks">
      <v-subheader v-if="secondaryHeader" class="pb-0">{{ secondaryHeader }}</v-subheader>
      <v-divider></v-divider>
      <v-list nav dense>
        <template v-for="nav in secondaryLinks">
          <!-- Multi Items -->
          <v-list-group
            v-if="nav.children"
            :key="nav.title + 'multi-item'"
            v-model="dropDowns[nav.title]"
            color="primary"
            :prepend-icon="nav.icon"
          >
            <template #activator>
              <v-list-item-title>{{ nav.title }}</v-list-item-title>
            </template>

            <v-list-item v-for="child in nav.children" :key="child.title" :to="child.to">
              <v-list-item-icon>
                <v-icon>{{ child.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ child.title }}</v-list-item-title>
            </v-list-item>
          </v-list-group>

          <!-- Single Item -->
          <v-list-item-group v-else :key="nav.title + 'single-item'" v-model="secondarySelected" color="primary">
            <v-list-item link :to="nav.to">
              <v-list-item-icon>
                <v-icon>{{ nav.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ nav.title }}</v-list-item-title>
            </v-list-item>
          </v-list-item-group>
        </template>
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
    secondaryHeader: {
      type: String,
      default: null,
    },
  },
  setup() {
    return {};
  },
  data() {
    return {
      dropDowns: {},
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
