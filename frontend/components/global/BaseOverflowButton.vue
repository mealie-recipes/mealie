<template>
  <v-menu offset-y>
    <template #activator="{ on, attrs }">
      <v-btn color="primary" v-bind="{ ...attrs, ...$attrs }" :class="btnClass" :disabled="disabled" v-on="on">
        <v-icon v-if="activeObj.icon" left>
          {{ activeObj.icon }}
        </v-icon>
        {{ mode === MODES.model ? activeObj.text : btnText }}
        <v-icon right>
          {{ $globals.icons.chevronDown }}
        </v-icon>
      </v-btn>
    </template>
    <!-- Model -->
    <v-list v-if="mode === MODES.model" dense>
      <v-list-item-group v-model="itemGroup">
        <template v-for="(item, index) in items">
          <div v-if="!item.hide" :key="index">
            <v-list-item @click="setValue(item)">
              <v-list-item-icon v-if="item.icon">
                <v-icon>{{ item.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ item.text }}</v-list-item-title>
            </v-list-item>
            <v-divider v-if="item.divider" :key="`divider-${index}`" class="my-1" ></v-divider>
          </div>
        </template>
      </v-list-item-group>
    </v-list>
    <!-- Links -->
    <v-list v-else-if="mode === MODES.link" dense>
      <v-list-item-group v-model="itemGroup">
        <template v-for="(item, index) in items">
          <div v-if="!item.hide" :key="index">
            <v-list-item :to="item.to">
            <v-list-item-icon v-if="item.icon">
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ item.text }}</v-list-item-title>
            </v-list-item>
            <v-divider v-if="item.divider" :key="`divider-${index}`" class="my-1" ></v-divider>
          </div>
        </template>
      </v-list-item-group>
    </v-list>
    <!-- Event -->
    <v-list v-else-if="mode === MODES.event" dense>
      <template v-for="(item, index) in items">
        <div v-if="!item.hide" :key="index">
          <v-list-item @click="$emit(item.event)">
            <v-list-item-icon v-if="item.icon">
              <v-icon>{{ item.icon }}</v-icon>
            </v-list-item-icon>
            <v-list-item-title>{{ item.text }}</v-list-item-title>
          </v-list-item>
          <v-divider v-if="item.divider" :key="`divider-${index}`" class="my-1" ></v-divider>
        </div>
      </template>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";

const INPUT_EVENT = "input";

type modes = "model" | "link" | "event";

const MODES = {
  model: "model",
  link: "link",
  event: "event",
};

export interface MenuItem {
  text: string;
  icon?: string;
  to?: string;
  value?: string;
  event?: string;
  divider?: boolean;
  hide?: boolean;
}

export default defineComponent({
  props: {
    mode: {
      type: String as () => modes,
      default: "model",
    },
    items: {
      type: Array as () => MenuItem[],
      required: true,
    },
    disabled: {
      type: Boolean,
      required: false,
      default: false,
    },
    value: {
      type: String,
      required: false,
      default: "",
    },
    btnClass: {
      type: String,
      required: false,
      default: "",
    },
    btnText: {
      type: String,
      required: false,
      default: function () {
        return this.$t("general.actions");
      }
    },
  },
  setup(props, context) {
    const activeObj = ref<MenuItem>({
      text: "DEFAULT",
      value: "",
    });

    let startIndex = 0;
    props.items.forEach((item, index) => {
      if (item.value === props.value) {
        startIndex = index;

        activeObj.value = item;
      }
    });
    const itemGroup = ref(startIndex);

    function setValue(v: MenuItem) {
      context.emit(INPUT_EVENT, v.value);
      activeObj.value = v;
    }

    return {
      MODES,
      activeObj,
      itemGroup,
      setValue,
    };
  },
});
</script>
