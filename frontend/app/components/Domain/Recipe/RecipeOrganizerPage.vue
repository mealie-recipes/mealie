<template>
  <div v-if="items" class="mealie-page">
    <RecipeOrganizerDialog
      v-model="dialogs.organizer"
      :item-type="itemType"
    />

    <BaseDialog
      v-if="deleteTarget"
      v-model="dialogs.delete"
      bottom-sheet
      :title="$t('general.delete-with-name', { name: $t(translationKey) })"
      color="error"
      :icon="$globals.icons.alertCircle"
      can-confirm
      @confirm="deleteOne()"
    >
      <v-card-text>
        <p>{{ $t("general.confirm-delete-generic-with-name", { name: $t(translationKey) }) }}</p>
        <p class="mt-4 mb-0 ml-4">
          {{ deleteTarget.name }}
        </p>
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-if="updateTarget"
      v-model="dialogs.update"
      :title="$t('general.update')"
      :icon="$globals.icons.edit"
      can-confirm
      @confirm="updateOne()"
    >
      <v-card-text>
        <v-text-field
          v-model="updateTarget.name"
          :label="$t('general.name')"
        />
        <v-checkbox
          v-if="itemType === Organizer.Tool"
          v-model="updateTarget.onHand"
          :label="$t('tool.on-hand')"
        />
      </v-card-text>
    </BaseDialog>

    <header class="mealie-page__header">
      <div class="mealie-page__titles">
        <div class="mealie-eyebrow">
          {{ $t("general.organizers") }} · {{ items.length }}
        </div>
        <h1 class="mealie-page__title">
          <slot name="title" />
        </h1>
      </div>
      <div class="mealie-page__actions">
        <label class="organizer-search">
          <v-icon size="16" class="organizer-search__icon">
            {{ $globals.icons.search }}
          </v-icon>
          <input
            v-model="searchString"
            type="search"
            class="organizer-search__input"
            :placeholder="$t('search.search-placeholder')"
            :aria-label="$t('search.search')"
            autofocus
          >
        </label>
        <button
          type="button"
          class="mealie-pill mealie-pill--primary"
          @click="dialogs.organizer = true"
        >
          <v-icon size="16">
            {{ $globals.icons.createAlt }}
          </v-icon>
          {{ $t("general.create") }}
        </button>
      </div>
    </header>

    <div class="mealie-page__body">
      <div v-if="!Object.keys(itemsSorted).length" class="organizer-empty mealie-card">
        {{ $t("search.no-results") }}
      </div>
      <section
        v-for="(itms, key, idx) in itemsSorted"
        :key="'header' + idx"
        class="organizer-section"
      >
        <h2 v-if="isTitle(key)" class="organizer-section__letter">
          {{ key }}
        </h2>
        <div class="organizer-grid">
          <template v-for="(item, index) in itms" :key="'cat' + index">
            <RouterLink
              v-if="item"
              class="organizer-tile"
              :to="`/g/${groupSlug}?${itemType}=${item.id}`"
            >
              <span class="organizer-tile__icon">
                <v-icon size="18">{{ icon }}</v-icon>
              </span>
              <span class="organizer-tile__text">
                <span class="organizer-tile__name">{{ item.name }}</span>
                <span v-if="item.recipeCount !== undefined" class="organizer-tile__count">
                  {{ $t("recipe-library.recipes-count", item.recipeCount) }}
                </span>
              </span>
              <ContextMenu
                class="organizer-tile__menu"
                :items="[presets.delete, presets.edit]"
                @delete="confirmDelete(item)"
                @edit="openUpdateDialog(item)"
              />
            </RouterLink>
          </template>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import Fuse from "fuse.js";
import { useContextPresets } from "~/composables/use-context-presents";
import RecipeOrganizerDialog from "~/components/Domain/Recipe/RecipeOrganizerDialog.vue";
import { Organizer, type RecipeOrganizer } from "~/lib/api/types/non-generated";
import { useRouteQuery } from "~/composables/use-router";
import { deepCopy } from "~/composables/use-utils";

interface GenericItem {
  id: string;
  name: string;
  slug: string;
  onHand: boolean;
  recipeCount?: number;
}

const props = defineProps<{
  items: GenericItem[];
  icon: string;
  itemType: RecipeOrganizer;
}>();

const emit = defineEmits<{
  update: [item: GenericItem];
  delete: [id: string];
}>();

const state = reactive({
  // Search Options
  options: {
    ignoreLocation: true,
    shouldSort: true,
    threshold: 0.2,
    location: 0,
    distance: 20,
    findAllMatches: true,
    maxPatternLength: 32,
    minMatchCharLength: 1,
    keys: ["name"],
  },
});

const auth = useMealieAuth();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user?.value?.groupSlug || "");

// =================================================================
// Context Menu

const dialogs = ref({
  organizer: false,
  update: false,
  delete: false,
});

const presets = useContextPresets();

const translationKey = computed<string>(() => {
  const typeMap = {
    categories: "category.category",
    tags: "tag.tag",
    tools: "tool.tool",
    foods: "shopping-list.food",
    households: "household.household",
  };
  return typeMap[props.itemType] || "";
});

const deleteTarget = ref<GenericItem | null>(null);
const updateTarget = ref<GenericItem | null>(null);

function confirmDelete(item: GenericItem) {
  deleteTarget.value = item;
  dialogs.value.delete = true;
}

function deleteOne() {
  if (!deleteTarget.value) {
    return;
  }

  emit("delete", deleteTarget.value.id);
}

function openUpdateDialog(item: GenericItem) {
  updateTarget.value = deepCopy(item);
  dialogs.value.update = true;
}

function updateOne() {
  if (!updateTarget.value) {
    return;
  }

  emit("update", updateTarget.value);
}

// ================================================================
// Search Functions

const searchString = useRouteQuery("q", "");

const fuse = computed(() => {
  return new Fuse(props.items, state.options);
});

const fuzzyItems = computed<GenericItem[]>(() => {
  if (searchString.value.trim() === "") {
    return props.items;
  }
  const result = fuse.value.search(searchString.value.trim() as string);
  return result.map(x => x.item);
});

// =================================================================
// Sorted Items

const itemsSorted = computed(() => {
  const byLetter: { [key: string]: Array<GenericItem> } = {};

  if (!fuzzyItems.value) {
    return byLetter;
  }

  [...fuzzyItems.value]
    .sort((a, b) => a.name.localeCompare(b.name))
    .forEach((item) => {
      const letter = item.name[0].toUpperCase();
      if (!byLetter[letter]) {
        byLetter[letter] = [];
      }
      byLetter[letter].push(item);
    });

  return byLetter;
});

function isTitle(str: number | string) {
  return typeof str === "string" && str.length === 1;
}
</script>

<style scoped>
.organizer-search {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 260px;
  max-width: 100%;
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  background: var(--mealie-fill);
  box-sizing: border-box;
  cursor: text;
}

.organizer-search:focus-within {
  box-shadow: 0 0 0 3px rgba(var(--v-theme-primary), 0.25);
}

.organizer-search__icon {
  color: var(--mealie-text-tertiary);
}

.organizer-search__input {
  flex: 1;
  min-width: 0;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--mealie-ink);
  font: inherit;
  font-size: 14px;
}

.organizer-search__input::placeholder {
  color: var(--mealie-text-tertiary);
  opacity: 1;
}

.organizer-section + .organizer-section {
  margin-top: 24px;
}

.organizer-section__letter {
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--mealie-hairline);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--mealie-text-tertiary);
}

.organizer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 10px;
}

.organizer-tile {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 60px;
  padding: 10px 6px 10px 12px;
  border-radius: 16px;
  background: var(--mealie-surface);
  box-shadow: inset 0 0 0 1px var(--mealie-hairline);
  color: var(--mealie-ink);
  text-decoration: none;
  transition: box-shadow 0.15s ease;
}

.organizer-tile:hover {
  box-shadow:
    inset 0 0 0 1px var(--mealie-hairline-strong),
    0 10px 24px -18px rgba(40, 30, 20, 0.4);
}

.organizer-tile:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.organizer-tile__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 10px;
  background: rgba(var(--v-theme-primary), 0.1);
  color: rgb(var(--v-theme-primary));
}

.organizer-tile__text {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.organizer-tile__name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  font-weight: 600;
}

.organizer-tile__count {
  font-size: 13px;
  color: var(--mealie-text-tertiary);
}

.organizer-tile__menu {
  flex-shrink: 0;
  color: var(--mealie-text-tertiary);
}

.organizer-empty {
  padding: 32px;
  text-align: center;
  color: var(--mealie-text-tertiary);
}

@media (max-width: 600px) {
  .organizer-search {
    flex: 1;
    width: auto;
  }
}
</style>
