<template>
  <header class="library-header">
    <div class="library-header__titles">
      <div class="mealie-eyebrow">
        {{ today }}
      </div>
      <h1 class="library-header__title">
        {{ $t("general.recipes") }}
      </h1>
    </div>
    <div class="library-header__actions">
      <label class="library-search">
        <v-icon size="16" class="library-search__icon">
          {{ $globals.icons.search }}
        </v-icon>
        <input
          ref="input"
          v-model="state.search"
          type="search"
          class="library-search__input"
          :placeholder="$t('recipe-library.search-placeholder')"
          :aria-label="$t('search.search')"
          enterkeyhint="search"
          @keyup.enter="onEnter"
          @keydown.esc="input?.blur()"
        >
        <kbd v-if="!state.search" class="mealie-kbd">{{ shortcutLabel }}</kbd>
        <button
          v-else
          type="button"
          class="library-search__clear"
          :aria-label="$t('search.clear-selection')"
          @click="state.search = ''"
        >
          <v-icon size="14">
            {{ $globals.icons.close }}
          </v-icon>
        </button>
      </label>
      <RecipeCreateMenu v-if="isOwnGroup">
        <template #activator="{ props: menuProps }">
          <button type="button" class="mealie-pill mealie-pill--primary" v-bind="menuProps">
            <v-icon size="16">
              {{ $globals.icons.createAlt }}
            </v-icon>
            {{ $t("recipe-library.new-recipe") }}
          </button>
        </template>
      </RecipeCreateMenu>
    </div>
  </header>
</template>

<script setup lang="ts">
import RecipeCreateMenu from "~/components/Domain/Recipe/RecipeCreateMenu.vue";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import { searchShortcutLabel, useGlobalSearch } from "~/composables/use-global-search";
import { useRecipeExplorerSearch } from "~/composables/use-recipe-explorer-search";

const auth = useMealieAuth();
const route = useRoute();
const i18n = useI18n();
const { isOwnGroup } = useLoggedInState();

const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");
const { state, search } = useRecipeExplorerSearch(groupSlug);

const input = ref<HTMLInputElement | null>(null);
const shortcutLabel = searchShortcutLabel();

// ⌘K and "/" focus this field instead of opening the quick-search dialog
const { registerPageSearch } = useGlobalSearch();
registerPageSearch(() => {
  input.value?.focus();
  input.value?.select();
});

const today = computed(() =>
  new Intl.DateTimeFormat(i18n.locale.value, { weekday: "long", month: "long", day: "numeric" }).format(new Date()),
);

function onEnter() {
  input.value?.blur();
  // with auto search off, results only refresh when asked to
  if (!state.value.auto) {
    search();
  }
}
</script>

<style scoped>
.library-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px 24px;
}

.library-header__titles {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.library-header__title {
  font-size: 34px;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.1;
  color: var(--mealie-ink);
}

.library-header__actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.library-search {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 300px;
  max-width: 100%;
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  background: var(--mealie-fill);
  box-sizing: border-box;
  cursor: text;
}

.library-search:focus-within {
  box-shadow: 0 0 0 3px rgba(var(--v-theme-primary), 0.25);
}

.library-search__icon {
  color: var(--mealie-text-tertiary);
}

.library-search__input {
  flex: 1;
  min-width: 0;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--mealie-ink);
  font: inherit;
  font-size: 14px;
}

.library-search__input::placeholder {
  color: var(--mealie-text-tertiary);
  opacity: 1;
}

.library-search__input::-webkit-search-cancel-button {
  display: none;
}

.library-search__clear {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 0;
  border-radius: 9px;
  background: var(--mealie-text-quaternary);
  color: var(--mealie-canvas);
  cursor: pointer;
}

@media (max-width: 600px) {
  .library-header__title {
    font-size: 28px;
  }

  .library-header__actions,
  .library-search {
    width: 100%;
  }

  .library-search {
    flex: 1;
  }
}
</style>
