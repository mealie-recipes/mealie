<template>
  <div>
    <v-card-text v-if="cookbook" class="px-1">
      <v-text-field v-model="cookbook.name" :label="$t('cookbook.cookbook-name')"></v-text-field>
      <v-textarea v-model="cookbook.description" auto-grow :rows="2" :label="$t('recipe.description')"></v-textarea>
      <QueryFieldBuilder
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
import { defineComponent } from "@nuxtjs/composition-api";
import { ReadCookBook } from "~/lib/api/types/cookbook";
import QueryFieldBuilder, { FieldDefinition } from "~/components/Domain/QueryFieldBuilder.vue";
export default defineComponent({
  components: { QueryFieldBuilder },
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
    function handleInput(value: string | undefined) {
      props.cookbook.queryFilterString = value || "";
    }

    const fieldDefs: FieldDefinition[] = [
      {
        name: "recipe_category.id",
        label: "Categories",
        type: "categories",
      },
      {
        name: "tags.id",
        label: "Tags",
        type: "tags",
      },
      {
        name: "tools.id",
        label: "Tools",
        type: "tools",
      },
      {
        name: "household_id",
        label: "Households",
        type: "households",
      },
    ];

    return {
      handleInput,
      fieldDefs,
    };
  },
});
</script>
