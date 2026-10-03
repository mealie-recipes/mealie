<template>
  <div>
    <div
      v-for="(part, index) in parts"
      :key="index"
      class="d-flex flex-wrap align-center py-1"
      style="gap: 4px"
    >
      <span v-if="index && part.logicalOperator">{{ part.logicalOperator }}</span>
      <span v-if="part.leftParenthesis">{{ part.leftParenthesis }}</span>
      <strong>{{ part.label }}</strong>
      <span>{{ part.relationalOperator }}</span>
      <template v-if="part.organizers">
        <v-chip
          v-for="organizer in part.organizers"
          :key="organizer.id"
          label
          color="accent"
          size="small"
        >
          {{ organizer.name }}
        </v-chip>
      </template>
      <span v-else>{{ part.value }}</span>
      <span v-if="part.rightParenthesis">{{ part.rightParenthesis }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { QueryFilterJSON } from "~/lib/api/types/non-generated";
import { useCategoryStore, useFoodStore, useHouseholdStore, useLabelStore, useTagStore, useToolStore } from "~/composables/store";
import { useUserStore } from "~/composables/store/use-user-store";
import { type FieldDefinition, type OrganizerBase, useQueryFilterBuilder } from "~/composables/use-query-filter-builder";
import { Organizer } from "~/lib/api/types/non-generated";

const props = defineProps<{
  fieldDefs: FieldDefinition[];
  queryFilter?: QueryFilterJSON | null;
}>();

const i18n = useI18n();
const { logOps, getRelOps, isOrganizerType } = useQueryFilterBuilder();

const storeMap = {
  [Organizer.Category]: useCategoryStore(),
  [Organizer.Tag]: useTagStore(),
  [Organizer.Tool]: useToolStore(),
  [Organizer.Food]: useFoodStore(),
  [Organizer.Label]: useLabelStore(),
  [Organizer.Household]: useHouseholdStore(),
  [Organizer.User]: useUserStore(),
};

function formatValue(fieldDef: FieldDefinition | undefined, value: string): string {
  if (fieldDef?.type === "date") {
    const date = new Date(value + "T00:00:00");
    return isNaN(date.getTime()) ? value : i18n.d(date);
  }

  if (fieldDef?.type === "relativeDate") {
    // Relative dates are stored as a negative offset in days, e.g. "$NOW-30d"
    const match = value.match(/^\$NOW-(\d+)d$/);
    if (match) {
      const days = parseInt(match[1]!);
      return `${days} ${i18n.t("query-filter.dates.days-ago", days)}`;
    }
  }

  return value;
}

const parts = computed(() => (props.queryFilter?.parts || []).map((part) => {
  const fieldDef = props.fieldDefs.find(fieldDef => fieldDef.name === part.attributeName);
  const values = Array.isArray(part.value) ? part.value : (part.value ? [part.value] : []);
  const relOp = part.relationalOperator;

  let organizers: OrganizerBase[] | undefined;
  if (fieldDef && isOrganizerType(fieldDef.type)) {
    const { store } = storeMap[fieldDef.type];
    organizers = values.map((value) => {
      const item = store.value.find(item => item?.id?.toString() === value);
      const name = item && ("fullName" in item ? item.fullName : item.name);
      return { id: value, name: name || value };
    });
  }

  return {
    leftParenthesis: part.leftParenthesis,
    rightParenthesis: part.rightParenthesis,
    logicalOperator: part.logicalOperator ? logOps.value[part.logicalOperator]?.label : undefined,
    label: fieldDef?.label || part.attributeName,
    relationalOperator: relOp && fieldDef ? getRelOps(fieldDef.type).value[relOp]?.label : relOp,
    organizers,
    value: values.map(value => formatValue(fieldDef, value)).join(", "),
  };
}));
</script>
