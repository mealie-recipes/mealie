<template>
  <v-menu offset-y>
    <template #activator="{ props: hoverProps }">
      <v-btn
        color="primary"
        v-bind="{ ...hoverProps, ...$attrs }"
        :class="btnClass"
        :disabled="disabled"
      >
        <v-icon
          v-if="activeObj.icon"
          start
        >
          {{ activeObj.icon }}
        </v-icon>
        {{ mode === MODES.model ? activeObj.text : btnText }}
        <v-icon end>
          {{ $globals.icons.chevronDown }}
        </v-icon>
      </v-btn>
    </template>
    <!-- Model -->
    <v-list
      v-if="mode === MODES.model"
      v-model:selected="itemGroup"
      density="compact"
    >
      <template v-for="(item, index) in items">
        <div
          v-if="!item.hide"
          :key="index"
        >
          <v-list-item @click="setValue(item)">
            <template
              v-if="item.icon"
              #prepend
            >
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.text }}</v-list-item-title>
          </v-list-item>
          <v-divider
            v-if="item.divider"
            :key="`divider-${index}`"
            class="my-1"
          />
        </div>
      </template>
    </v-list>
    <!-- Links -->
    <v-list
      v-else-if="mode === MODES.link"
      v-model:selected="itemGroup"
      density="compact"
    >
      <template v-for="(item, index) in items">
        <div
          v-if="!item.hide"
          :key="index"
        >
          <v-list-item :to="item.to">
            <template
              v-if="item.icon"
              #prepend
            >
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.text }}</v-list-item-title>
          </v-list-item>
          <v-divider
            v-if="item.divider"
            :key="`divider-${index}`"
            class="my-1"
          />
        </div>
      </template>
    </v-list>
    <!-- Event -->
    <v-list
      v-else-if="mode === MODES.event"
      density="compact"
    >
      <template v-for="(item, index) in items">
        <div
          v-if="!item.hide"
          :key="index"
        >
          <v-list-item @click="$emit(item.event)">
            <template
              v-if="item.icon"
              #prepend
            >
              <v-icon>{{ item.icon }}</v-icon>
            </template>
            <v-list-item-title>{{ item.text }}</v-list-item-title>
          </v-list-item>
          <v-divider
            v-if="item.divider"
            :key="`divider-${index}`"
            class="my-1"
          />
        </div>
      </template>
    </v-list>
  </v-menu>
</template>

<script setup lang="ts">
const MODES = {
  model: "model",
  link: "link",
  event: "event",
};

type modes = "model" | "link" | "event";

export interface MenuItem {
  text: string;
  icon?: string;
  to?: string;
  value?: string;
  event?: string;
  divider?: boolean;
  hide?: boolean;
}

const props = defineProps({
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
  btnClass: {
    type: String,
    required: false,
    default: "",
  },
  btnText: {
    type: String,
    required: false,
    default: function () {
      return useI18n().t("general.actions");
    },
  },
});

const modelValue = defineModel({
  type: String,
  required: false,
  default: "",
});

const activeObj = ref<MenuItem>({
  text: "DEFAULT",
  value: "",
});

let startIndex = 0;
props.items.forEach((item, index) => {
  if (item.value === modelValue.value) {
    startIndex = index;

    activeObj.value = item;
  }
});
const itemGroup = ref(startIndex);

function setValue(v: MenuItem) {
  modelValue.value = v.value || "";
  activeObj.value = v;
}
</script>
