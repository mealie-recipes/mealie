<template>
  <div
    v-if="shoppingListChoices && ready"
    class="mealie-page mealie-page--narrow"
  >
    <BaseDialog
      v-model="state.createDialog"
      bottom-sheet
      :title="$t('shopping-list.create-shopping-list')"
      :icon="$globals.icons.formatListCheck"
      can-submit
      :submit-disabled="!isCreateNameValid"
      @submit="createOne"
    >
      <v-card-text>
        <v-text-field
          v-model.trim="state.createName"
          autofocus
          :label="$t('shopping-list.new-list')"
        />
      </v-card-text>
    </BaseDialog>

    <!-- Settings -->
    <BaseDialog
      v-model="state.ownerDialog"
      bottom-sheet
      :icon="$globals.icons.admin"
      :title="$t('user.edit-user')"
      can-confirm
      @confirm="updateOwner"
    >
      <v-container>
        <v-form>
          <v-select
            v-model="updateUserId"
            :items="allUsers"
            item-title="fullName"
            item-value="id"
            :label="$t('general.owner')"
            :prepend-icon="$globals.icons.user"
          />
        </v-form>
      </v-container>
    </BaseDialog>

    <BaseDialog
      v-model="state.deleteDialog"
      bottom-sheet
      :title="$t('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteOne"
    >
      <v-card-text>{{ $t('shopping-list.are-you-sure-you-want-to-delete-this-item') }}</v-card-text>
    </BaseDialog>
    <header class="mealie-page__header">
      <div class="mealie-page__titles">
        <div class="mealie-eyebrow">
          {{ $t("shopping-list.list-count", shoppingListChoices.length) }}
        </div>
        <h1 class="mealie-page__title">
          {{ $t('shopping-list.shopping-lists') }}
        </h1>
      </div>
      <div class="mealie-page__actions">
        <v-checkbox
          v-model="preferences.viewAllLists"
          hide-details
          density="compact"
          color="primary"
          :label="$t('general.show-all')"
          class="my-0"
        />
        <button
          type="button"
          class="mealie-pill mealie-pill--primary"
          @click="state.createDialog = true"
        >
          <v-icon size="16">
            {{ $globals.icons.createAlt }}
          </v-icon>
          {{ $t('shopping-list.new-list') }}
        </button>
      </div>
    </header>

    <div class="mealie-page__body">
      <div v-if="!shoppingListChoices.length" class="lists-empty mealie-card">
        {{ $t('shopping-list.no-shopping-lists-found') }}
      </div>

      <nav v-else class="lists mealie-card">
        <RouterLink
          v-for="list in shoppingListChoices"
          :key="list.id"
          class="lists__row"
          :to="`/shopping-lists/${list.id}`"
        >
          <span class="lists__icon">
            <v-icon size="18">
              {{ $globals.icons.formatListBulleted }}
            </v-icon>
          </span>
          <span class="lists__name">{{ list.name }}</span>
          <button
            type="button"
            class="lists__action"
            :aria-label="$t('general.owner')"
            :title="$t('general.owner')"
            @click.prevent="toggleOwnerDialog(list)"
          >
            <v-icon size="18">
              {{ $globals.icons.user }}
            </v-icon>
          </button>
          <button
            type="button"
            class="lists__action"
            :aria-label="$t('general.delete')"
            :title="$t('general.delete')"
            @click.prevent="openDelete(list.id)"
          >
            <v-icon size="18">
              {{ $globals.icons.delete }}
            </v-icon>
          </button>
          <v-icon size="16" class="lists__chevron">
            {{ $globals.icons.chevronRight }}
          </v-icon>
        </RouterLink>
      </nav>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ShoppingListOut } from "~/lib/api/types/household";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";
import { useShoppingListPreferences } from "~/composables/use-users/preferences";
import type { UserOut } from "~/lib/api/types/user";

definePageMeta({
  middleware: ["auth"],
});

const auth = useMealieAuth();
const i18n = useI18n();
const ready = ref(false);
const userApi = useUserApi();
const route = useRoute();

useSeoMeta({
  title: i18n.t("shopping-list.shopping-list"),
});

const overrideDisableRedirect = ref(false);
const disableRedirect = computed(() => route.query.disableRedirect === "true" || overrideDisableRedirect.value);
const preferences = useShoppingListPreferences();

const state = reactive({
  createName: "",
  createDialog: false,
  deleteDialog: false,
  deleteTarget: "",
  ownerDialog: false,
  ownerTarget: ref<ShoppingListOut | null>(null),
});
const isCreateNameValid = computed(() => state.createName.trim().length > 0);

const { data: shoppingLists } = useAsyncData(useAsyncKey(), async () => {
  return await fetchShoppingLists();
});

const shoppingListChoices = computed(() => {
  if (!shoppingLists.value) {
    return [];
  }

  return shoppingLists.value.filter(list => preferences.value.viewAllLists || list.userId === auth.user.value?.id);
});

// This has to appear before the shoppingListChoices watcher, otherwise that runs first and the redirect is not disabled
watch(
  () => preferences.value.viewAllLists,
  () => {
    overrideDisableRedirect.value = true;
  },
);

watch(
  () => shoppingListChoices,
  () => {
    if (!disableRedirect.value && shoppingListChoices.value.length === 1) {
      navigateTo(`/shopping-lists/${shoppingListChoices.value[0].id}`);
    }
    else {
      ready.value = true;
    }
  },
  {
    deep: true,
  },
);

async function fetchShoppingLists() {
  const { data } = await userApi.shopping.lists.getAll(1, -1, { orderBy: "name", orderDirection: "asc" });

  if (!data) {
    return [];
  }

  return data.items;
}

async function refresh() {
  shoppingLists.value = await fetchShoppingLists();
}

async function createOne() {
  if (!isCreateNameValid.value) return;
  const { data } = await userApi.shopping.lists.createOne({ name: state.createName.trim() });

  if (data) {
    refresh();
    state.createName = "";
  }
}

async function toggleOwnerDialog(list: ShoppingListOut) {
  if (!state.ownerDialog) {
    state.ownerTarget = list;
    await fetchAllUsers();
  }
  state.ownerDialog = !state.ownerDialog;
}

// ===============================================================
// Shopping List Edit User/Owner

const allUsers = ref<UserOut[]>([]);
const updateUserId = ref<string | undefined>();
async function fetchAllUsers() {
  const { data } = await userApi.households.fetchMembers();
  if (!data) {
    return;
  }

  // update current user
  allUsers.value = data.items.sort((a, b) => ((a.fullName || "") < (b.fullName || "") ? -1 : 1));
  updateUserId.value = state.ownerTarget?.userId;
}

async function updateOwner() {
  if (!state.ownerTarget || !updateUserId.value) {
    return;
  }
  // user has not changed, so we should not update
  if (state.ownerTarget.userId === updateUserId.value) {
    return;
  }
  // get full list, so the move does not delete shopping list items
  const { data: fullList } = await userApi.shopping.lists.getOne(state.ownerTarget.id);
  if (!fullList) {
    return;
  }
  const { data } = await userApi.shopping.lists.updateOne(
    state.ownerTarget.id,
    { ...fullList, userId: updateUserId.value },
  );

  if (data) {
    refresh();
  }
}

function openDelete(id: string) {
  state.deleteDialog = true;
  state.deleteTarget = id;
}

async function deleteOne() {
  const { data } = await userApi.shopping.lists.deleteOne(state.deleteTarget);
  if (data) {
    refresh();
  }
}
</script>

<style scoped>
.lists {
  display: flex;
  flex-direction: column;
  padding: 6px;
}

.lists__row {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 56px;
  padding: 0 10px 0 12px;
  border-radius: 16px;
  color: var(--mealie-ink);
  text-decoration: none;
}

.lists__row + .lists__row {
  box-shadow: 0 -1px 0 var(--mealie-hairline);
}

.lists__row:hover {
  background: var(--mealie-fill-subtle);
}

.lists__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  border-radius: 10px;
  background: rgba(var(--v-theme-primary), 0.12);
  color: rgb(var(--v-theme-primary));
}

.lists__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 16px;
  font-weight: 600;
}

.lists__action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 0;
  border-radius: 16px;
  background: transparent;
  color: var(--mealie-text-tertiary);
  cursor: pointer;
}

.lists__action:hover {
  background: var(--mealie-fill);
  color: var(--mealie-ink);
}

.lists__chevron {
  color: var(--mealie-text-quaternary);
}

.lists-empty {
  padding: 32px;
  text-align: center;
  color: var(--mealie-text-tertiary);
}
</style>
