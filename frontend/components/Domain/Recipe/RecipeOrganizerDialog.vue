<template>
  <div>
    <BaseDialog
      v-model="dialog"
      width="500"
      :title="properties.title"
      :icon="properties.icon"
      can-submit
      :submit-disabled="!name"
      @submit="select"
    >
      <v-form>
        <v-card-text>
          <v-text-field
            v-model="name"
            :label="properties.label"
            :rules="[rules.required]"
            autofocus
          />
          <v-checkbox
            v-if="itemType === Organizer.Tool"
            v-model="onHand"
            :label="$t('tool.on-hand')"
          />
        </v-card-text>
      </v-form>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import { useCategoryStore, useTagStore, useToolStore } from "~/composables/store";
import { type RecipeOrganizer, Organizer } from "~/lib/api/types/non-generated";

const { $globals } = useNuxtApp();

const CREATED_ITEM_EVENT = "created-item";

interface Props {
  color?: string | null;
  tagDialog?: boolean;
  itemType?: RecipeOrganizer;
}
const props = withDefaults(defineProps<Props>(), {
  color: null,
  tagDialog: true,
  itemType: "category" as RecipeOrganizer,
});

const emit = defineEmits<{
  "created-item": [item: any];
}>();

const dialog = defineModel<boolean>({ default: false });

const i18n = useI18n();

const name = ref("");
const onHand = ref(false);

watch(
  dialog,
  (val: boolean) => {
    if (!val) name.value = "";
  },
);

const userApi = useUserApi();

const store = (() => {
  switch (props.itemType) {
    case Organizer.Tag:
      return useTagStore();
    case Organizer.Tool:
      return useToolStore();
    default:
      return useCategoryStore();
  }
})();

const properties = computed(() => {
  switch (props.itemType) {
    case Organizer.Tag:
      return {
        title: i18n.t("tag.create-a-tag"),
        label: i18n.t("tag.tag-name"),
        icon: $globals.icons.tags,
        api: userApi.tags,
      };
    case Organizer.Tool:
      return {
        title: i18n.t("tool.create-a-tool"),
        label: i18n.t("tool.tool-name"),
        icon: $globals.icons.potSteam,
        api: userApi.tools,
      };
    default:
      return {
        title: i18n.t("category.create-a-category"),
        label: i18n.t("category.category-name"),
        icon: $globals.icons.categories,
        api: userApi.categories,
      };
  }
});

const rules = {
  required: (val: string) => !!val || (i18n.t("general.a-name-is-required") as string),
};

async function select() {
  if (store) {
    // @ts-expect-error the same state is used for different organizer types, which have different requirements
    const newItem = await store.actions.createOne({ name: name.value, onHand: onHand.value });
    emit(CREATED_ITEM_EVENT, newItem);
  }
  dialog.value = false;
}
</script>

<style></style>
