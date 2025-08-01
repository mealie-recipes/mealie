<template>
  <div>
    <v-card-text
      v-if="cookbook"
      class="px-1"
    >
      <v-text-field
        v-model="cookbook.name"
        :label="$t('cookbook.cookbook-name')"
        variant="underlined"
        color="primary"
      />
      <v-textarea
        v-model="cookbook.description"
        auto-grow
        :rows="2"
        :label="$t('recipe.description')"
        variant="underlined"
        color="primary"
      />
      <QueryFilterBuilder
        :field-defs="fieldDefs"
        :initial-query-filter="cookbook.queryFilter"
        @input="handleInput"
      />
      <v-switch
        v-model="cookbook.public"
        hide-details
        single-line
        color="primary"
      >
        <template #label>
          {{ $t('cookbook.public-cookbook') }}
          <HelpIcon
            size="small"
            right
            class="ml-2"
          >
            {{ $t('cookbook.public-cookbook-description') }}
          </HelpIcon>
        </template>
      </v-switch>
    </v-card-text>
  </div>
</template>

<script setup lang="ts">
import { Organizer } from "~/lib/api/types/non-generated";
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import type { FieldDefinition } from "~/composables/use-query-filter-builder";
import type { ReadCookBook } from "~/lib/api/types/cookbook";

const modelValue = defineModel<ReadCookBook>({ required: true });
const i18n = useI18n();
const cookbook = toRef(modelValue);
function handleInput(value: string | undefined) {
  cookbook.value.queryFilterString = value || "";
}

const fieldDefs: FieldDefinition[] = [
  {
    name: "recipe_category.id",
    label: i18n.t("category.categories"),
    type: Organizer.Category,
  },
  {
    name: "tags.id",
    label: i18n.t("tag.tags"),
    type: Organizer.Tag,
  },
  {
    name: "recipe_ingredient.food.id",
    label: i18n.t("recipe.ingredients"),
    type: Organizer.Food,
  },
  {
    name: "tools.id",
    label: i18n.t("tool.tools"),
    type: Organizer.Tool,
  },
  {
    name: "household_id",
    label: i18n.t("household.households"),
    type: Organizer.Household,
  },
  {
    name: "created_at",
    label: i18n.t("general.date-created"),
    type: "date",
  },
  {
    name: "updated_at",
    label: i18n.t("general.date-updated"),
    type: "date",
  },
];
</script>
