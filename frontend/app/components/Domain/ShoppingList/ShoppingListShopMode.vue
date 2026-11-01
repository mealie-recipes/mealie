<template>
  <section class="shop-mode">
    <!-- stays in view while scrolling, so the close button never covers a row -->
    <header class="shop-mode__header">
      <h2 class="text-h5 shop-mode__title">
        {{ listName }}
      </h2>
      <div class="shop-mode__remaining">
        {{ $t("shopping-list.shop-mode-items-left", { count: remainingCount }) }}
      </div>
      <v-btn
        icon
        color="primary"
        class="shop-mode__close"
        :aria-label="$t('general.close')"
        @click="emit('close')"
      >
        <v-icon>{{ $globals.icons.close }}</v-icon>
      </v-btn>
    </header>

    <v-switch
      v-model="showChecked"
      class="shop-mode__switch"
      color="primary"
      density="compact"
      hide-details
      :label="$t('shopping-list.shop-mode-show-completed', { count: checkedItems.length })"
    />

    <div v-for="section in sections" :key="section.label" class="shop-mode__section">
      <div
        class="shop-mode__section-title"
        :style="getLabelColor(section.label) ? { borderInlineStartColor: getLabelColor(section.label) } : undefined"
      >
        {{ section.label }} · {{ section.items.length }}
      </div>
      <ShoppingListShopItem
        v-for="item in section.items"
        :key="item.id"
        :item="item"
        @tap="onTap"
      />
    </div>

    <div v-if="showChecked && checkedItems.length" class="shop-mode__section shop-mode__section--checked">
      <div class="shop-mode__section-title">
        {{ $t("shopping-list.shop-mode-completed-section", { count: checkedItems.length }) }}
      </div>
      <ShoppingListShopItem
        v-for="item in checkedItems"
        :key="item.id"
        :item="item"
        @tap="onTap"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import ShoppingListShopItem from "~/components/Domain/ShoppingList/ShoppingListShopItem.vue";
import type { ShopModeSection } from "~/composables/shopping-list-page/sub-composables/use-shopping-list-shop-mode";
import type { ShoppingListItemOut } from "~/lib/api/types/household";

// A checked row leaves the list, moving the next one under the finger. This window spans the whole
// list rather than a single row, so the second tap of a double tap can't check the next item.
const TAP_GUARD_MS = 400;

defineProps<{
  listName: string;
  sections: ShopModeSection[];
  checkedItems: ShoppingListItemOut[];
  remainingCount: number;
  getLabelColor: (label: string) => string | undefined;
}>();

const showChecked = defineModel<boolean>("showChecked", { default: false });

const emit = defineEmits<{
  toggle: [item: ShoppingListItemOut];
  close: [];
}>();

let lastTap = Number.NEGATIVE_INFINITY;

function onTap(item: ShoppingListItemOut) {
  const now = Date.now();
  if (now - lastTap < TAP_GUARD_MS) {
    return;
  }
  lastTap = now;
  emit("toggle", item);
}
</script>

<style scoped>
.shop-mode {
  padding-bottom: 72px;
}

/* the app bar is 48px high */
.shop-mode__header {
  position: sticky;
  top: 48px;
  z-index: 1;
  padding: 8px 12px;
  border-bottom: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgb(var(--v-theme-background));
}

.shop-mode__close {
  position: absolute;
  top: 8px;
  inset-inline-end: 0;
}

.shop-mode__switch {
  padding: 0 12px;
}

/* leave room for the fixed close button */
.shop-mode__title,
.shop-mode__remaining {
  padding-inline-end: 56px;
  overflow-wrap: anywhere;
}

/* the header stays on screen, so it has to stay small */
.shop-mode__title {
  margin: 0;
  line-height: 1.3 !important;
}

.shop-mode__remaining {
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.3;
}

/* label on the left and switch on the right, with the whole row tappable */
.shop-mode__switch :deep(.v-selection-control) {
  flex-direction: row-reverse;
  justify-content: space-between;
}

.shop-mode__switch :deep(.v-label) {
  padding-inline-start: 0;
  opacity: 1;
}

.shop-mode__section-title {
  padding: 8px 12px 8px 8px;
  border-inline-start: 4px solid transparent;
  border-bottom: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  font-weight: 700;
}
</style>
