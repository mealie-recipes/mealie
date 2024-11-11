<template>
  <div>
    <v-card-text v-if="cookbook" class="px-1">
      <v-text-field v-model="cookbook.name" :label="$t('cookbook.cookbook-name')"></v-text-field>
      <v-textarea v-model="cookbook.description" auto-grow :rows="2" :label="$t('recipe.description')"></v-textarea>
      <QueryFilterBuilder
        :field-defs="fieldDefs"
        :initial-query-filter="cookbook.queryFilter"
        @input="handleInput"
      />
      <v-switch v-model="cookbook.public" hide-details single-line>
        <template #label>
          {{ $t('cookbook.public-cookbook') }}
          <HelpIcon small right class="ml-2">
            {{ $t('cookbook.public-cookbook-description') }}
          </HelpIcon>
        </template>
      </v-switch>
    </v-card-text>
  </div>
</template>

<script lang="ts">
import { defineComponent, useContext } from "@nuxtjs/composition-api";
import { ReadCookBook } from "~/lib/api/types/cookbook";
import { Organizer } from "~/lib/api/types/non-generated";
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import { FieldDefinition } from "~/composables/use-query-filter-builder";

export default defineComponent({
  components: { QueryFilterBuilder },
  props: {
    cookbook: {
      type: Object as () => ReadCookBook,
      required: true,
    },
    actions: {
      type: Object as () => any,
      required: true,
    },
  },
  setup(props) {
    const { i18n } = useContext();

    function handleInput(value: string | undefined) {
      props.cookbook.queryFilterString = value || "";
    }

    const fieldDefs: FieldDefinition[] = [
      {
        name: "recipe_category.id",
        label: i18n.tc("category.categories"),
        type: Organizer.Category,
      },
      {
        name: "tags.id",
        label: i18n.tc("tag.tags"),
        type: Organizer.Tag,
      },
      {
        name: "recipe_ingredient.food.id",
        label: i18n.tc("recipe.ingredients"),
        type: Organizer.Food,
      },
      {
        name: "tools.id",
        label: i18n.tc("tool.tools"),
        type: Organizer.Tool,
      },
      {
        name: "household_id",
        label: i18n.tc("household.households"),
        type: Organizer.Household,
      },
      {
        name: "created_at",
        label: i18n.tc("general.date-created"),
        type: "date",
      },
      {
        name: "updated_at",
        label: i18n.tc("general.date-updated"),
        type: "date",
      },
    ];

    return {
      handleInput,
      fieldDefs,
    };
  },
});
</script>
