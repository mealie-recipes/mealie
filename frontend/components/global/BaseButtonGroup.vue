<template>
  <v-item-group>
    <template v-for="btn in buttons">
      <v-menu v-if="btn.children" :key="'menu-' + btn.event" active-class="pa-0" offset-y top left :style="stretch ? 'width: 100%;' : ''">
        <template #activator="{ on, attrs }">
          <v-btn tile :large="large" icon v-bind="attrs" v-on="on">
            <v-icon>
              {{ btn.icon }}
            </v-icon>
          </v-btn>
        </template>
        <v-list dense>
          <template v-for="(child, idx) in btn.children">
            <v-list-item :key="idx" dense @click="$emit(child.event)">
              <v-list-item-title>{{ child.text }}</v-list-item-title>
            </v-list-item>
            <v-divider v-if="child.divider" :key="`divider-${idx}`" class="my-1"></v-divider>
          </template>
        </v-list>
      </v-menu>
      <v-tooltip
        v-else
        :key="'btn-' + btn.event"
        open-delay="200"
        transition="slide-y-reverse-transition"
        dense
        bottom
        content-class="text-caption"
      >
        <template #activator="{ on, attrs }">
          <v-btn
            tile
            icon
            :color="btn.color"
            :large="large"
            :disabled="btn.disabled"
            :style="stretch ? `width: ${maxButtonWidth};` : ''"
            v-bind="attrs"
            v-on="on"
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
import { computed, defineComponent } from "@nuxtjs/composition-api";

export interface ButtonOption {
  icon?: string;
  color?: string;
  text: string;
  event: string;
  children?: ButtonOption[];
  disabled?: boolean;
  divider?: boolean;
}

export default defineComponent({
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
    }
  },
  setup(props) {
    const maxButtonWidth = computed(() => `${100 / props.buttons.length}%`);
    return {
      maxButtonWidth,
    };
  }
});
</script>
