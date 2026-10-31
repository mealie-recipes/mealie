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
import QueryFilterBuilder from "~/components/Domain/QueryFilterBuilder.vue";
import { useRecipeFilterFields } from "~/composables/use-recipe-filter-fields";
import type { ReadCookBook } from "~/lib/api/types/cookbook";

const modelValue = defineModel<ReadCookBook>({ required: true });
const cookbook = toRef(modelValue);
function handleInput(value: string | undefined) {
  cookbook.value.queryFilterString = value || "";
}

const fieldDefs = useRecipeFilterFields();
</script>
