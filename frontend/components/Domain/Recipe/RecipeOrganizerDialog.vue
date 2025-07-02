<template>
  <div>
    <v-dialog
      v-model="dialog"
      width="500"
    >
      <v-card>
        <v-app-bar
          density="compact"
          dark
          color="primary mb-2 position-relative left-0 top-0 w-100 pl-3"
        >
          <v-icon
            size="large"
            start
            class="mt-1"
          >
            {{ itemType === Organizer.Tool ? $globals.icons.potSteam
              : itemType === Organizer.Category ? $globals.icons.categories
                : $globals.icons.tags }}
          </v-icon>

          <v-toolbar-title class="headline">
            {{ properties.title }}
          </v-toolbar-title>

          <v-spacer />
        </v-app-bar>
        <v-card-title />
        <v-form @submit.prevent="select">
          <v-card-text>
            <v-text-field
              v-model="name"
              density="compact"
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
          <v-card-actions>
            <BaseButton
              cancel
              @click="dialog = false"
            />
            <v-spacer />
            <BaseButton
              type="submit"
              create
              :disabled="!name"
            />
          </v-card-actions>
        </v-form>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import { useUserApi } from "~/composables/api";
import { useCategoryStore, useTagStore, useToolStore } from "~/composables/store";
import { type RecipeOrganizer, Organizer } from "~/lib/api/types/non-generated";

const CREATED_ITEM_EVENT = "created-item";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Boolean,
      default: false,
    },
    color: {
      type: String,
      default: null,
    },
    tagDialog: {
      type: Boolean,
      default: true,
    },
    itemType: {
      type: String as () => RecipeOrganizer,
      default: "category",
    },
  },
  emits: ["update:modelValue"],
  setup(props, context) {
    const i18n = useI18n();

    const state = reactive({
      name: "",
      onHand: false,
    });

    const dialog = computed({
      get() {
        return props.modelValue;
      },
      set(value) {
        context.emit("update:modelValue", value);
      },
    });

    watch(
      () => props.modelValue,
      (val: boolean) => {
        if (!val) state.name = "";
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
            api: userApi.tags,
          };
        case Organizer.Tool:
          return {
            title: i18n.t("tool.create-a-tool"),
            label: i18n.t("tool.tool-name"),
            api: userApi.tools,
          };
        default:
          return {
            title: i18n.t("category.create-a-category"),
            label: i18n.t("category.category-name"),
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
        await store.actions.createOne({ ...state });
      }

      const newItem = store.store.value.find(item => item.name === state.name);

      context.emit(CREATED_ITEM_EVENT, newItem);
      dialog.value = false;
    }

    return {
      Organizer,
      ...toRefs(state),
      dialog,
      properties,
      rules,
      select,
    };
  },
});
</script>

<style></style>
