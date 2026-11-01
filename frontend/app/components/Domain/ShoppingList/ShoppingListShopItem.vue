<template>
  <div
    class="shop-item"
    :class="{ 'shop-item--checked': item.checked }"
    role="button"
    tabindex="0"
    :aria-pressed="item.checked ? 'true' : 'false'"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointercancel="onPointerCancel"
    @click="onClick"
    @keydown.enter.prevent="emit('tap', item)"
    @keydown.space.prevent="emit('tap', item)"
  >
    <v-icon class="shop-item__box" :color="item.checked ? 'primary' : undefined">
      {{ item.checked ? "$checkboxOn" : "$checkboxOff" }}
    </v-icon>
    <div class="shop-item__text">
      <SafeMarkdown v-if="title" class="shop-item__name" :source="title" />
      <SafeMarkdown v-if="note" class="shop-item__note text-truncate" :source="note" />
    </div>
    <div v-if="parsed.quantity || parsed.unit" class="shop-item__amount">
      <SafeMarkdown v-if="parsed.quantity" class="shop-item__quantity" :source="parsed.quantity" />
      <span v-if="parsed.unit" class="shop-item__unit">{{ parsed.unit }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useIngredientTextParser } from "~/composables/recipes";
import type { RecipeIngredient, ShoppingListItemOut } from "~/lib/api/types/household";

// same threshold as the swipe detection in ShoppingListItem
const MOVE_THRESHOLD = 8;

const props = defineProps<{
  item: ShoppingListItemOut;
}>();

const emit = defineEmits<{
  tap: [item: ShoppingListItemOut];
}>();

const { useParsedIngredientText } = useIngredientTextParser();
const parsed = computed(() => useParsedIngredientText(props.item as RecipeIngredient));

// an item without a food only has its note, so that's what the row is called
const title = computed(() => parsed.value.name || parsed.value.note);
const note = computed(() => (parsed.value.name ? parsed.value.note : undefined));

let start: { x: number; y: number } | null = null;
let moved = false;

function onPointerDown(event: PointerEvent) {
  start = { x: event.clientX, y: event.clientY };
  moved = false;
}

function onPointerMove(event: PointerEvent) {
  if (!start || moved) {
    return;
  }
  moved = Math.abs(event.clientX - start.x) > MOVE_THRESHOLD || Math.abs(event.clientY - start.y) > MOVE_THRESHOLD;
}

// the browser took the touch over, e.g. to scroll
function onPointerCancel() {
  moved = true;
}

function onClick() {
  const ignore = moved;
  start = null;
  moved = false;
  if (!ignore) {
    emit("tap", props.item);
  }
}
</script>

<style scoped>
.shop-item {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 56px;
  padding: 6px 12px;
  border-bottom: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: transparent;
  touch-action: manipulation;
}

.shop-item:active {
  background: rgba(var(--v-theme-on-surface), 0.08);
}

.shop-item--checked {
  background: rgba(var(--v-theme-on-surface), 0.04);
}

.shop-item__box {
  flex-shrink: 0;
}

.shop-item__text {
  flex: 1 1 auto;
  min-width: 0;
}

/* links in a name or note must not catch the tap meant for the row */
.shop-item__text,
.shop-item__amount {
  pointer-events: none;
}

.shop-item__name {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.3;
  overflow-wrap: anywhere;
}

.shop-item__note {
  font-size: 0.875rem;
  line-height: 1.3;
  opacity: 0.7;
}

.shop-item__note :deep(p),
.shop-item__note :deep(ul),
.shop-item__note :deep(ol),
.shop-item__note :deep(li) {
  display: inline;
}

.shop-item__note :deep(br) {
  display: none;
}

.shop-item__amount {
  display: flex;
  align-items: baseline;
  gap: 0.25em;
  flex-shrink: 0;
  font-size: 1.0625rem;
  font-weight: 500;
  white-space: nowrap;
}

.shop-item__quantity :deep(p) {
  display: inline;
}

.shop-item--checked .shop-item__name {
  text-decoration: line-through;
  opacity: 0.6;
}

.shop-item--checked .shop-item__amount {
  opacity: 0.6;
}
</style>
