<template>
  <div style="overflow-x: hidden;">
    <v-container
      v-if="!edit"
      class="pa-0"
      :style="{
        transform: `translateX(${isRtl ? -swiping : swiping}px)`,
        transition: swiping === 0 ? 'transform 0.2s ease' : 'none',
        opacity: swiping >= SWIPE_THRESHOLD ? 0.5 : 1,
      }"
    >
      <v-row
        ref="swipeRowRef"
        v-touch="{ move: onSwipeMove, start: onSwipeStart, end: onSwipeEnd }"
        style="touch-action: pan-y;"
        no-gutters
        class="flex-nowrap align-center"
      >
        <v-col :cols="itemLabelCols">
          <div class="d-flex align-center flex-nowrap">
            <v-checkbox
              :model-value="listItem.checked"
              hide-details
              density="compact"
              class="mt-0 flex-shrink-0"
              color="null"
              @click="toggleChecked"
            />
            <div
              class="ml-2 text-truncate"
              :class="listItem.checked ? 'strike-through' : ''"
              style="min-width: 0;"
            >
              <RecipeIngredientListItem :ingredient="listItem" />
            </div>
          </div>
        </v-col>
        <v-spacer />
        <v-col
          cols="auto"
          class="text-right"
        >
          <div
            v-if="!listItem.checked"
            style="min-width: 72px"
          >
            <v-menu
              offset-x
              start
              min-width="125px"
            >
              <template #activator="{ props: hoverProps }">
                <v-tooltip
                  v-if="recipeList && recipeList.length"
                  open-delay="200"
                  transition="slide-x-reverse-transition"
                  density="compact"
                  location="end"
                  content-class="text-caption"
                >
                  <template #activator="{ props: tooltipProps }">
                    <v-btn
                      size="small"
                      variant="text"
                      class="ml-2"
                      icon
                      v-bind="tooltipProps"
                      @click="displayRecipeRefs = !displayRecipeRefs"
                    >
                      <v-icon>
                        {{ $globals.icons.silverwareForkKnife }}
                      </v-icon>
                    </v-btn>
                  </template>
                  <span>Toggle Recipes</span>
                </v-tooltip>
                <v-btn
                  size="small"
                  variant="text"
                  class="ml-2"
                  icon
                  @click="toggleEdit(!edit)"
                >
                  <v-icon>
                    {{ $globals.icons.edit }}
                  </v-icon>
                </v-btn>
                <v-btn
                  size="small"
                  variant="text"
                  class="handle"
                  icon
                  v-bind="hoverProps"
                >
                  <v-icon>
                    {{ $globals.icons.arrowUpDown }}
                  </v-icon>
                </v-btn>
              </template>
              <v-list density="compact">
                <v-list-item
                  v-for="action in contextMenu"
                  :key="action.event"
                  density="compact"
                  @click="contextHandler(action.event)"
                >
                  <v-list-item-title>
                    {{ action.text }}
                  </v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
        </v-col>
      </v-row>
      <v-container
        v-if="!listItem.checked && recipeList && recipeList.length && displayRecipeRefs"
        class="pa-0"
      >
        <RecipeList
          :recipes="recipeList"
          :list-item="listItem"
          :disabled="isOffline"
          :tile="true"
        />
      </v-container>
      <v-row
        v-if="listItem.checked"
        no-gutters
        class="mb-2"
      >
        <v-col cols="auto">
          <div class="text-caption font-weight-light font-italic">
            {{ $t("shopping-list.completed-on", {
              date: listItem.updatedAt ? $d(new Date(listItem.updatedAt)) : '',
            }) }}
          </div>
        </v-col>
      </v-row>
    </v-container>
    <div
      v-if="edit"
      class="mb-4"
    >
      <ShoppingListItemEditor
        v-model="localListItem"
        :labels="labels"
        :units="units"
        :foods="foods"
        class="ma-2"
        @save="save"
        @cancel="toggleEdit(false)"
        @delete="$emit('delete')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useOnline } from "@vueuse/core";
import RecipeIngredientListItem from "../Recipe/RecipeIngredientListItem.vue";
import ShoppingListItemEditor from "./ShoppingListItemEditor.vue";
import RecipeList from "~/components/Domain/Recipe/RecipeList.vue";
import type { ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { IngredientUnit, IngredientFood, RecipeSummary } from "~/lib/api/types/recipe";

const model = defineModel<ShoppingListItemOut>({ type: Object as () => ShoppingListItemOut, required: true });

const props = defineProps({
  labels: {
    type: Array as () => MultiPurposeLabelOut[],
    required: true,
  },
  units: {
    type: Array as () => IngredientUnit[],
    required: true,
  },
  foods: {
    type: Array as () => IngredientFood[],
    required: true,
  },
  recipes: {
    type: Map as unknown as () => Map<string, RecipeSummary>,
    default: undefined,
  },
});

const emit = defineEmits<{
  (e: "checked" | "save", item: ShoppingListItemOut): void;
  (e: "delete"): void;
}>();

const SWIPE_THRESHOLD = 50;

const { isRtl } = useRtl();
const swipeRowRef = ref<InstanceType<typeof import("vuetify/components").VRow> | null>(null);

onMounted(() => {
  const el = swipeRowRef.value?.$el as HTMLElement | undefined;
  if (!el) return;
  el.addEventListener(
    "touchmove",
    (e: TouchEvent) => {
      if (swipeInfo.value.gesture === "swipe") {
        e.preventDefault();
      }
    },
    { passive: false },
  );
});
const i18n = useI18n();
const displayRecipeRefs = ref(false);
const itemLabelCols = computed<string>(() => (model.value?.checked ? "auto" : "6"));
const online = useOnline();
const isOffline = computed(() => online.value === false);

type actions = { text: string; event: string };
const contextMenu = ref<actions[]>([
  { text: i18n.t("general.edit") as string, event: "edit" },
  { text: i18n.t("general.delete") as string, event: "delete" },
]);

// copy prop value so a refresh doesn't interrupt the user
const localListItem = ref(Object.assign({}, model.value));

const listItem = computed<ShoppingListItemOut>({
  get: () => model.value,
  set: (val: ShoppingListItemOut) => {
    localListItem.value = val;
    model.value = val;
  },
});

const edit = ref(false);
function toggleEdit(val = !edit.value) {
  if (edit.value === val) return;
  if (val) localListItem.value = model.value;
  edit.value = val;
}

function toggleChecked() {
  const updated = { ...model.value, checked: !model.value.checked } as ShoppingListItemOut;
  model.value = updated;
  emit("checked", updated);
}

function contextHandler(event: string) {
  if (event === "edit") {
    toggleEdit(true);
  }
  else {
    emit(event as any);
  }
}

function save() {
  emit("save", localListItem.value);
  edit.value = false;
}

type SwipeGesture = null | "scroll" | "swipe";

const swipeInfo = ref({
  touchstartX: 0,
  touchstartY: 0,
  touchendX: 0,
  touchendY: 0,
  gesture: null as SwipeGesture,
});

function getSwipePoint(e: any) {
  const touch = e?.touches?.[0] ?? e?.changedTouches?.[0] ?? e;
  return { x: touch?.clientX ?? 0, y: touch?.clientY ?? 0 };
}

function resetSwipe() {
  swipeInfo.value = { touchstartX: 0, touchstartY: 0, touchendX: 0, touchendY: 0, gesture: null };
}

function onSwipeStart(payload: any) {
  const { x, y } = getSwipePoint(payload.originalEvent);
  swipeInfo.value = { touchstartX: x, touchstartY: y, touchendX: x, touchendY: y, gesture: null };
}

function onSwipeMove(payload: any) {
  const { x, y } = getSwipePoint(payload.originalEvent);
  swipeInfo.value.touchendX = x;
  swipeInfo.value.touchendY = y;

  if (!swipeInfo.value.gesture) {
    const deltaX = Math.abs(x - swipeInfo.value.touchstartX);
    const deltaY = Math.abs(y - swipeInfo.value.touchstartY);
    if (deltaY > 8 && deltaY > deltaX) {
      swipeInfo.value.gesture = "scroll";
    }
    else if (deltaX > 8 && deltaX > deltaY) {
      swipeInfo.value.gesture = "swipe";
    }
    else if (deltaX > 8 || deltaY > 8) {
      // Diagonal / ambiguous — default to scroll
      swipeInfo.value.gesture = "scroll";
    }
  }
}

function onSwipeEnd() {
  if (swipeInfo.value.gesture === "swipe" && swiping.value >= SWIPE_THRESHOLD) {
    toggleChecked();
  }
  resetSwipe();
}

const swiping = computed(() => {
  if (swipeInfo.value.gesture !== "swipe") {
    return 0;
  }
  const deltaX = isRtl.value
    ? swipeInfo.value.touchstartX - swipeInfo.value.touchendX
    : swipeInfo.value.touchendX - swipeInfo.value.touchstartX;
  return Math.max(0, Math.min(deltaX, 100));
});

const recipeList = computed<RecipeSummary[]>(() => {
  const ret: RecipeSummary[] = [];
  if (!listItem.value.recipeReferences) return ret;
  listItem.value.recipeReferences.forEach((ref) => {
    const recipe = props.recipes?.get(ref.recipeId);
    if (recipe) ret.push(recipe);
  });
  return ret;
});
</script>

<style lang="css">
.strike-through {
  text-decoration: line-through !important;
}
</style>
