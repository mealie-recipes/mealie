<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-if="createTarget"
      v-model="dialogStates.create"
      width="100%"
      max-width="1100px"
      :icon="$globals.icons.pages"
      :title="$t('cookbook.create-a-cookbook')"
      :submit-icon="$globals.icons.save"
      :submit-text="$t('general.save')"
      :submit-disabled="!createTarget.name?.trim() || !createTarget.queryFilterString"
      can-submit
      disable-submit-on-enter
      @submit="actions.updateOne(createTarget)"
      @cancel="deleteCreateTarget()"
    >
      <v-card-text>
        <CookbookEditor :key="createTargetKey" v-model="createTarget" />
      </v-card-text>
    </BaseDialog>

    <!-- Edit Dialog -->
    <BaseDialog
      v-if="editTarget"
      v-model="dialogStates.edit"
      width="100%"
      max-width="1100px"
      :icon="$globals.icons.pages"
      :title="$t('general.edit')"
      :submit-icon="$globals.icons.save"
      :submit-text="$t('general.save')"
      :submit-disabled="!editTarget.name?.trim() || !editTarget.queryFilterString"
      can-submit
      can-delete
      @submit="actions.updateOne(editTarget)"
      @delete="deleteEventHandler(editTarget)"
    >
      <v-card-text>
        <CookbookEditor v-model="editTarget" />
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="dialogStates.delete"
      bottom-sheet
      :title="$t('general.delete-with-name', { name: $t('cookbook.cookbook') })"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      @confirm="deleteCookbook()"
    >
      <v-card-text>
        <p>{{ $t("general.confirm-delete-generic-with-name", { name: $t("cookbook.cookbook") }) }}</p>
        <p v-if="deleteTarget" class="mt-4 ml-4">
          {{ deleteTarget.name }}
        </p>
      </v-card-text>
    </BaseDialog>

    <!-- Cookbook Page -->
    <!-- Page Title -->
    <v-container class="lg-container">
      <BasePageTitle divider>
        <template #header>
          <v-img width="100%" max-height="100" max-width="100" src="/svgs/manage-cookbooks.svg" />
        </template>
        <template #title>
          {{ $t("cookbook.cookbooks") }}
        </template>
        {{ $t("cookbook.description") }}
      </BasePageTitle>

      <div class="my-6">
        <v-checkbox
          v-model="cookbookPreferences.hideOtherHouseholds"
          :label="$t('cookbook.hide-cookbooks-from-other-households')"
          hide-details
          color="primary"
        />
        <div class="ml-10 mt-n3">
          <p class="text-subtitle-2 my-0 py-0">
            {{ $t("cookbook.hide-cookbooks-from-other-households-description") }}
          </p>
        </div>
      </div>

      <!-- Create New -->
      <BaseButton create @click="createCookbook" />

      <!-- Cookbook List -->
      <VueDraggable
        v-model="myCookbooks"
        handle=".handle"
        :delay="250"
        :delay-on-touch-only="true"
        class="mt-2"
        @end="updateAll(myCookbooks)"
      >
        <v-card
          v-for="cookbook in myCookbooks"
          :key="cookbook.id"
          class="my-2 left-border"
        >
          <v-card-title class="d-flex align-center text-h6 opacity-80">
            <v-icon size="large" start>
              {{ $globals.icons.pages }}
            </v-icon>
            {{ cookbook.name }}
            <v-spacer />
            <v-btn
              icon
              variant="text"
              class="ml-2"
              :title="$t('general.edit')"
              @click="editEventHandler(cookbook)"
            >
              <v-icon>
                {{ $globals.icons.edit }}
              </v-icon>
            </v-btn>
            <v-icon class="handle" :size="40">
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </v-card-title>
        </v-card>
      </VueDraggable>
    </v-container>
  </div>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { useCookbookStore } from "~/composables/store/use-cookbook-store";
import { useHouseholdSelf } from "@/composables/use-households";
import CookbookEditor from "~/components/Domain/Cookbook/CookbookEditor.vue";
import type { CookBookCreate, CookBookOut } from "~/lib/api/types/cookbook";
import { useCookbookPreferences } from "~/composables/use-users/preferences";

definePageMeta({
  middleware: ["auth", "group-only"],
});

const dialogStates = reactive({
  create: false,
  edit: false,
  delete: false,
});

const i18n = useI18n();

// Set page title
useSeoMeta({
  title: i18n.t("cookbook.cookbooks"),
});

const auth = useMealieAuth();
const { store: allCookbooks, actions, updateAll } = useCookbookStore();

// Make a local reactive copy of myCookbooks
const myCookbooks = ref<CookBookOut[]>([]);
watch(
  allCookbooks,
  (cookbooks) => {
    myCookbooks.value
      = cookbooks?.filter(
        cookbook => cookbook.householdId === auth.user.value?.householdId,
      ).sort((a, b) => a.position > b.position) ?? [];
  },
  { immediate: true },
);

const { household } = useHouseholdSelf();
const cookbookPreferences = useCookbookPreferences();

// create
const createTargetKey = ref(0);
const createTarget = ref<CookBookOut | null>(null);
async function createCookbook() {
  const name = i18n.t("cookbook.household-cookbook-name", [
    household.value?.name || "",
    String((myCookbooks.value?.length ?? 0) + 1),
  ]) as string;

  const data = { name } as CookBookCreate;
  await actions.createOne(data).then((cookbook) => {
    if (!cookbook) {
      return;
    }

    myCookbooks.value.push(cookbook);
    createTarget.value = cookbook as CookBookOut;
    createTargetKey.value++;
  });
  dialogStates.create = true;
}

// edit
const editTarget = ref<ReadCookBook | null>(null);
function editEventHandler(item: ReadCookBook) {
  // edit a copy, so cancelling the dialog discards the changes
  editTarget.value = structuredClone(toRaw(item));
  dialogStates.edit = true;
}

// delete
const deleteTarget = ref<CookBookOut | null>(null);
function deleteEventHandler(item: CookBookOut) {
  deleteTarget.value = item;
  dialogStates.delete = true;
}
async function deleteCookbook() {
  if (!deleteTarget.value) {
    return;
  }
  await actions.deleteOne(deleteTarget.value.id);
  myCookbooks.value = myCookbooks.value.filter(c => c.id !== deleteTarget.value?.id);
  dialogStates.delete = false;
  deleteTarget.value = null;
}

async function deleteCreateTarget() {
  if (!createTarget.value?.id) {
    return;
  }
  await actions.deleteOne(createTarget.value.id);
  myCookbooks.value = myCookbooks.value.filter(c => c.id !== createTarget.value?.id);
  dialogStates.create = false;
  createTarget.value = null;
}
function handleUnmount() {
  if (!createTarget.value?.id || createTarget.value.queryFilterString) {
    return;
  }
  deleteCreateTarget();
}
onMounted(() => {
  window.addEventListener("beforeunload", handleUnmount);
});
onBeforeUnmount(() => {
  handleUnmount();
  window.removeEventListener("beforeunload", handleUnmount);
});
</script>
