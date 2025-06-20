<template>
  <v-item-group>
    <template v-for="btn in buttons">
      <v-menu
        v-if="btn.children"
        :key="'menu-' + btn.event"
        active-class="pa-0"
        offset-y
        top
        start
        :style="stretch ? 'width: 100%;' : ''"
      >
        <template #activator="{ props }">
          <v-btn
            tile
            :large="large"
            icon
            variant="plain"
            v-bind="props"
          >
            <v-icon>
              {{ btn.icon }}
            </v-icon>
          </v-btn>
        </template>
        <v-list density="compact">
          <template
            v-for="(child, idx) in btn.children"
            :key="idx"
          >
            <v-list-item
              density="compact"
              @click="$emit(child.event)"
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
      <v-tooltip
        v-else
        :key="'btn-' + btn.event"
        open-delay="200"
        transition="slide-y-reverse-transition"
        density="compact"
        bottom
        content-class="text-caption"
      >
        <template #activator="{ props }">
          <v-btn
            tile
            icon
            :color="btn.color"
            :large="large"
            :disabled="btn.disabled"
            :style="stretch ? `width: ${maxButtonWidth};` : ''"
            variant="plain"
            v-bind="props"
            @click="$emit(btn.event)"
          >
            <v-icon> {{ btn.icon }} </v-icon>
          </v-btn>
        </template>
        <span>{{ btn.text }}</span>
      </v-tooltip>
    </template>
  </v-item-group>
</template>

<script lang="ts">
export interface ButtonOption {
  icon?: string;
  color?: string;
  text: string;
  event: string;
  children?: ButtonOption[];
  disabled?: boolean;
  divider?: boolean;
}

export default defineNuxtComponent({
  props: {
    buttons: {
      type: Array as () => ButtonOption[],
      required: true,
    },
    large: {
      type: Boolean,
      default: true,
    },
    stretch: {
      type: Boolean,
      default: false,
    },
  },
  setup(props) {
    const maxButtonWidth = computed(() => `${100 / props.buttons.length}%`);
    return {
      maxButtonWidth,
    };
  },
});
</script>
