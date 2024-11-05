<template>
  <v-navigation-drawer v-model="drawer" class="d-flex flex-column d-print-none" clipped app width="240px">
    <!-- User Profile -->
    <template v-if="loggedIn">
      <v-list-item two-line :to="userProfileLink" exact>
        <UserAvatar list :user-id="$auth.user.id" :tooltip="false" />

        <v-list-item-content>
          <v-list-item-title class="pr-2"> {{ $auth.user.fullName }}</v-list-item-title>
          <v-list-item-subtitle>
            <v-btn v-if="isOwnGroup" class="px-2 pa-0" text :to="userFavoritesLink" small>
              <v-icon left small>
                {{ $globals.icons.heart }}
              </v-icon>
              {{ $t("user.favorite-recipes") }}
            </v-btn>
          </v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
      <v-divider></v-divider>
    </template>

    <slot></slot>

    <!-- Primary Links -->
    <template v-if="topLink">
      <v-list nav dense>
        <template v-for="nav in topLink">
          <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
            <!-- Multi Items -->
            <v-list-group
              v-if="nav.children"
              :key="(nav.key || nav.title) + 'multi-item'"
              v-model="dropDowns[nav.title]"
              color="primary"
              :prepend-icon="nav.icon"
            >
              <template #activator>
                <v-list-item-title>{{ nav.title }}</v-list-item-title>
              </template>

              <v-list-item v-for="child in nav.children" :key="child.key || child.title" exact :to="child.to" class="ml-2">
                <v-list-item-icon>
                  <v-icon>{{ child.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ child.title }}</v-list-item-title>
              </v-list-item>
            </v-list-group>

            <!-- Single Item -->
            <v-list-item-group
              v-else
              :key="(nav.key || nav.title) + 'single-item'"
              v-model="secondarySelected"
              color="primary"
            >
              <v-list-item exact link :to="nav.to">
                <v-list-item-icon>
                  <v-icon>{{ nav.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ nav.title }}</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </div>
        </template>
      </v-list>
    </template>

    <!-- Secondary Links -->
    <template v-if="secondaryLinks.length > 0">
      <v-divider class="mt-2"></v-divider>
      <v-list nav dense exact>
        <template v-for="nav in secondaryLinks">
          <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
            <!-- Multi Items -->
            <v-list-group
              v-if="nav.children"
              :key="(nav.key || nav.title) + 'multi-item'"
              v-model="dropDowns[nav.title]"
              color="primary"
              :prepend-icon="nav.icon"
            >
              <template #activator>
                <v-list-item-title>{{ nav.title }}</v-list-item-title>
              </template>

              <v-list-item v-for="child in nav.children" :key="child.key || child.title" exact :to="child.to" class="ml-2">
                <v-list-item-icon>
                  <v-icon>{{ child.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ child.title }}</v-list-item-title>
              </v-list-item>
            </v-list-group>

            <!-- Single Item -->
            <v-list-item-group v-else :key="(nav.key || nav.title) + 'single-item'" v-model="secondarySelected" color="primary">
              <v-list-item exact link :to="nav.to">
                <v-list-item-icon>
                  <v-icon>{{ nav.icon }}</v-icon>
                </v-list-item-icon>
                <v-list-item-title>{{ nav.title }}</v-list-item-title>
              </v-list-item>
            </v-list-item-group>
          </div>
        </template>
      </v-list>
    </template>

    <!-- Bottom Navigation Links -->
    <template v-if="bottomLinks" #append>
      <v-list nav dense>
        <v-list-item-group v-model="bottomSelected" color="primary">
          <template v-for="nav in bottomLinks">
            <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
              <v-list-item
                :key="nav.key || nav.title"
                exact
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
            </div>
          </template>
        </v-list-item-group>
        <slot name="bottom"></slot>
      </v-list>
    </template>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, toRefs, useContext, watch } from "@nuxtjs/composition-api";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { SidebarLinks } from "~/types/application-types";
import UserAvatar from "~/components/Domain/User/UserAvatar.vue";

export default defineComponent({
  components: {
    UserAvatar,
  },
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
  setup(props, context) {
    // V-Model Support
    const drawer = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        if (window.innerWidth < 760 && state.hasOpenedBefore === false) {
          state.hasOpenedBefore = true;
          val = false;
          context.emit("input", val);
        } else {
          context.emit("input", val);
        }
      },
    });

    const { $auth } = useContext();
    const { loggedIn, isOwnGroup } = useLoggedInState();

    const userFavoritesLink = computed(() => $auth.user ? `/user/${$auth.user.id}/favorites` : undefined);
    const userProfileLink = computed(() => $auth.user ? "/user/profile" : undefined);

    const state = reactive({
      dropDowns: {} as Record<string, boolean>,
      topSelected: null as string[] | null,
      secondarySelected: null as string[] | null,
      bottomSelected: null as string[] | null,
      hasOpenedBefore: false as boolean,
    });

    const allLinks = computed(() => [...props.topLink, ...(props.secondaryLinks || []), ...(props.bottomLinks || [])]);
    function initDropdowns() {
      allLinks.value.forEach((link) => {
        state.dropDowns[link.title] = link.childrenStartExpanded || false;
      })
    }
    watch(
      () => allLinks,
      () => {
        initDropdowns();
      },
      {
        deep: true,
      }
    );

    return {
      ...toRefs(state),
      userFavoritesLink,
      userProfileLink,
      drawer,
      loggedIn,
      isOwnGroup,
    };
  },
});
</script>

<style>
@media print {
  .no-print {
    display: none;
  }
}

.favorites-link {
  text-decoration: none;
}

.favorites-link:hover {
  text-decoration: underline;
}
</style>
