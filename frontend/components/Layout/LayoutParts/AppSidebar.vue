<template>
  <v-navigation-drawer v-model="showDrawer" class="d-flex flex-column d-print-none position-fixed" touchless>
    <slot />

    <!-- Primary Links -->
    <template v-if="topLink">
      <v-list v-model:selected="secondarySelected" nav density="comfortable" color="primary">
        <template v-for="nav in topLink">
          <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
            <!-- Multi Items -->
            <v-list-group
              v-if="nav.children"
              :key="(nav.key || nav.title) + 'multi-item'"
              v-model="dropDowns[nav.title]"
              color="primary"
              :prepend-icon="nav.icon"
              :fluid="true"
            >
              <template #activator="{ props }">
                <v-list-item v-bind="props" :prepend-icon="nav.icon" :title="nav.title" />
              </template>

              <v-list-item
                v-for="child in nav.children"
                :key="child.key || child.title"
                exact
                :to="child.to"
                :prepend-icon="child.icon"
                :title="child.title"
                class="ml-4"
              />
            </v-list-group>

            <!-- Single Item -->
            <template v-else>
              <v-list-item
                :key="(nav.key || nav.title) + 'single-item'"
                exact
                link
                :to="nav.to"
                :prepend-icon="nav.icon"
                :title="nav.title"
              />
            </template>
          </div>
        </template>
      </v-list>
    </template>

    <!-- Secondary Links -->
    <template v-if="secondaryLinks.length > 0">
      <v-divider class="mt-2" />
      <v-list v-model:selected="secondarySelected" nav density="compact" exact>
        <template v-for="nav in secondaryLinks">
          <div v-if="!nav.restricted || isOwnGroup" :key="nav.key || nav.title">
            <!-- Multi Items -->
            <v-list-group
              v-if="nav.children"
              :key="(nav.key || nav.title) + 'multi-item'"
              v-model="dropDowns[nav.title]"
              color="primary"
              :prepend-icon="nav.icon"
              fluid
            >
              <template #activator="{ props }">
                <v-list-item v-bind="props" :prepend-icon="nav.icon" :title="nav.title" />
              </template>

              <v-list-item
                v-for="child in nav.children"
                :key="child.key || child.title"
                exact
                :to="child.to"
                class="ml-2"
                :prepend-icon="child.icon"
                :title="child.title"
              />
            </v-list-group>

            <!-- Single Item -->
            <v-list-item v-else :key="(nav.key || nav.title) + 'single-item'" exact link :to="nav.to">
              <template #prepend>
                <v-icon>{{ nav.icon }}</v-icon>
              </template>
              <v-list-item-title>{{ nav.title }}</v-list-item-title>
            </v-list-item>
          </div>
        </template>
      </v-list>
    </template>
  </v-navigation-drawer>
</template>

<script lang="ts">
import { useLoggedInState } from "~/composables/use-logged-in-state";
import type { SidebarLinks } from "~/types/application-types";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Boolean,
      required: false,
      default: false,
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
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const { isOwnGroup } = useLoggedInState();

    const state = reactive({
      dropDowns: {} as Record<string, boolean>,
      topSelected: null as string[] | null,
      secondarySelected: null as string[] | null,
    });
    // model to control the drawer
    const showDrawer = computed({
      get: () => props.modelValue,
      set: value => context.emit("update:modelValue", value),
    });

    const allLinks = computed(() => [...props.topLink, ...(props.secondaryLinks || [])]);
    function initDropdowns() {
      allLinks.value.forEach((link) => {
        state.dropDowns[link.title] = link.childrenStartExpanded || false;
      });
    }
    watch(
      () => allLinks,
      () => {
        initDropdowns();
      },
      {
        deep: true,
      },
    );

    return {
      ...toRefs(state),
      showDrawer,
      isOwnGroup,
    };
  },
});
</script>

<style scoped>
@media print {
  .no-print {
    display: none;
  }
}
</style>
