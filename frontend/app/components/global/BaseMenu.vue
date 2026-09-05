<template>
  <!-- the list already scrolls when the overlay is bounded, but nothing bounds it by default,
       so a menu taller than the screen simply runs off the bottom -->
  <v-menu
    :key="'menu-' + activator.event"
    active-class="pa-0"
    start
    max-height="80vh"
    :style="stretch ? 'width: 100%;' : ''"
  >
    <template #activator="{ props: hoverProps }">
      <slot name="activator" v-bind="{ props: hoverProps }">
        <v-btn
          tile
          :large="large"
          icon
          :color="activator.color"
          variant="plain"
          v-bind="hoverProps"
          :loading="activator.loading || children.some(({ loading }) => loading)"
        >
          <v-icon>
            {{ activator.icon }}
          </v-icon>
        </v-btn>
      </slot>
    </template>
    <v-list density="compact">
      <template
        v-for="(child, idx) in children"
        :key="idx"
      >
        <BaseMenu
          v-if="child.children"
          :activator="child"
          :children="child.children"
          open-on-hover
          open-on-focus
          open-on-click
          submenu
          @menu="(childEvent) => $emit('menu', childEvent)"
        >
          <template #activator="{ props: hoverProps }">
            <v-list-item
              density="compact"
              :prepend-icon="child.icon"
              :disabled="child.disabled"
              v-bind="hoverProps"
            >
              <v-list-item-title>{{ child.text }}</v-list-item-title>
            </v-list-item>
          </template>
        </BaseMenu>
        <v-list-item
          v-else
          density="compact"
          :prepend-icon="child.icon"
          :disabled="child.disabled"
          @click="$emit('menu', child.event)"
        >
          <v-list-item-title>{{ child.text }}</v-list-item-title>
        </v-list-item>
        <v-divider
          v-if="child.divider"
          :key="`divider-${idx}`"
          class="my-1"
        />
      </template>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
export interface ButtonOption {
  icon?: string;
  color?: string;
  text: string;
  event: string;
  children?: ButtonOption[];
  disabled?: boolean;
  divider?: boolean;
  loading?: boolean;
}

defineEmits<{
  menu: [string];
}>();

withDefaults(defineProps<{
  activator: ButtonOption;
  children: ButtonOption[];
  large?: boolean;
  stretch?: boolean;
}>(), {
  large: true,
  stretch: false,
});
</script>
