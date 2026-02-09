<template>
  <v-card class="ma-0" flat fluid>
    <v-card-text class="ma-0 pa-0">
      <VueDraggable
        v-model="fields"
        handle=".handle"
        :delay="250"
        :delay-on-touch-only="true"
        v-bind="{
          animation: 200,
          group: 'recipe-instructions',
          ghostClass: 'ghost',
        }"
        @start="drag = true"
        @end="onDragEnd"
      >
        <v-row
          v-for="(field, index) in fields"
          :key="field.id"
          class="d-flex flex-row flex-wrap mx-auto pb-2"
          :class="$vuetify.display.xs ? (Math.floor(index / 1) % 2 === 0 ? 'bg-dark' : 'bg-light') : ''"
          style="max-width: 100%;"
        >
          <!-- drag handle -->
          <v-col
            :cols="config.items.icon.cols(index)"
            :sm="config.items.icon.sm(index)"
            :class="$vuetify.display.smAndDown ? 'd-flex pa-0' : 'd-flex justify-end pr-6'"
          >
            <v-icon class="handle my-auto" :size="28" style="cursor: move;">
              {{ $globals.icons.arrowUpDown }}
            </v-icon>
          </v-col>

          <!-- and / or  -->
          <v-col
            v-if="index != 0 || $vuetify.display.smAndUp"
            :cols="config.items.logicalOperator.cols(index)"
            :sm="config.items.logicalOperator.sm(index)"
            :class="config.col.class"
          >
            <v-select
              v-if="index"
              :model-value="field.logicalOperator"
              :items="[logOps.AND, logOps.OR]"
              item-title="label"
              item-value="value"
              variant="underlined"
              @update:model-value="setLogicalOperatorValue(field, index, $event as unknown as LogicalOperator)"
            >
              <template #chip="{ item }">
                <span :class="config.select.textClass" style="width: 100%;">
                  {{ item.raw.label }}
                </span>
              </template>
            </v-select>
          </v-col>

          <!-- left parenthesis -->
          <v-col
            v-if="showAdvanced"
            :cols="config.items.leftParens.cols(index)"
            :sm="config.items.leftParens.sm(index)"
            :class="config.col.class"
          >
            <v-select
              :model-value="field.leftParenthesis"
              :items="['', '(', '((', '(((']"
              variant="underlined"
              @update:model-value="setLeftParenthesisValue(field, index, $event)"
            >
              <template #chip="{ item }">
                <span :class="config.select.textClass" style="width: 100%;">
                  {{ item.raw }}
                </span>
              </template>
            </v-select>
          </v-col>

          <!-- field name -->
          <v-col
            :cols="config.items.fieldName.cols(index)"
            :sm="config.items.fieldName.sm(index)"
            :class="config.col.class"
          >
            <v-select
              chips
              :model-value="field.label"
              :items="fieldDefs"
              variant="underlined"
              item-title="label"
              @update:model-value="setField(index, $event)"
            >
              <template #chip="{ item }">
                <span :class="config.select.textClass" style="width: 100%;">
                  {{ item.raw.label }}
                </span>
              </template>
            </v-select>
          </v-col>

          <!-- relational operator -->
          <v-col
            :cols="config.items.relationalOperator.cols(index)"
            :sm="config.items.relationalOperator.sm(index)"
            :class="config.col.class"
          >
            <v-select
              v-if="field.type !== 'boolean'"
              :model-value="field.relationalOperatorValue"
              :items="field.relationalOperatorChoices"
              item-title="label"
              item-value="value"
              variant="underlined"
              @update:model-value="setRelationalOperatorValue(field, index, $event as unknown as RelationalKeyword | RelationalOperator)"
            >
              <template #chip="{ item }">
                <span :class="config.select.textClass" style="width: 100%;">
                  {{ item.raw.label }}
                </span>
              </template>
            </v-select>
          </v-col>

          <!-- field value -->
          <v-col
            :cols="config.items.fieldValue.cols(index)"
            :sm="config.items.fieldValue.sm(index)"
            :class="config.col.class"
          >
            <v-select
              v-if="field.fieldChoices"
              :model-value="field.values"
              :items="field.fieldChoices"
              item-title="label"
              item-value="value"
              multiple
              variant="underlined"
              @update:model-value="setFieldValues(field, index, $event)"
            />
            <v-text-field
              v-else-if="field.type === 'string'"
              :model-value="field.value"
              variant="underlined"
              @update:model-value="setFieldValue(field, index, $event)"
            />
            <v-number-input
              v-else-if="field.type === 'number'"
              :model-value="field.value"
              variant="underlined"
              control-variant="stacked"
              inset
              :precision="null"
              @update:model-value="setFieldValue(field, index, $event)"
            />
            <v-checkbox
              v-else-if="field.type === 'boolean'"
              :model-value="field.value"
              @update:model-value="setFieldValue(field, index, $event!)"
            />
            <v-menu
              v-else-if="field.type === 'date'"
              v-model="datePickers[index]"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              max-width="290px"
              min-width="auto"
            >
              <template #activator="{ props: activatorProps }">
                <v-text-field
                  :model-value="$d(safeNewDate(field.value + 'T00:00:00'))"
                  variant="underlined"
                  color="primary"
                  class="date-input"
                  v-bind="activatorProps"
                  readonly
                />
              </template>
              <v-date-picker
                :model-value="safeNewDate(field.value + 'T00:00:00')"
                hide-header
                :first-day-of-week="firstDayOfWeek"
                :local="$i18n.locale"
                @update:model-value="val => setFieldValue(field, index, val ? val.toISOString().slice(0, 10) : '')"
              />
            </v-menu>
            <!--
              Relative dates are assumed to be negative intervals with a unit of days.
              The input is a *positive*, interpreted internally as a *negative* offset.
            -->
            <v-number-input
              v-else-if="field.type === 'relativeDate'"
              :model-value="parseRelativeDateOffset(field.value)"
              :suffix="$t('query-filter.dates.days-ago', parseRelativeDateOffset(field.value))"
              variant="underlined"
              control-variant="stacked"
              density="compact"
              inset
              :min="0"
              :precision="0"
              class="date-input"
              @update:model-value="setFieldValue(field, index, $event)"
            />
            <RecipeOrganizerSelector
              v-else-if="field.type === Organizer.Category"
              v-model="field.organizers"
              :selector-type="Organizer.Category"
              :show-add="false"
              :show-label="false"
              :show-icon="false"
              variant="underlined"
              @update:model-value="val => setFieldOrganizers(field, index, (val || []) as OrganizerBase[])"
            />
            <RecipeOrganizerSelector
              v-else-if="field.type === Organizer.Tag"
              v-model="field.organizers"
              :selector-type="Organizer.Tag"
              :show-add="false"
              :show-label="false"
              :show-icon="false"
              variant="underlined"
              @update:model-value="val => setFieldOrganizers(field, index, (val || []) as OrganizerBase[])"
            />
            <RecipeOrganizerSelector
              v-else-if="field.type === Organizer.Tool"
              v-model="field.organizers"
              :selector-type="Organizer.Tool"
              :show-add="false"
              :show-label="false"
              :show-icon="false"
              variant="underlined"
              @update:model-value="val => setFieldOrganizers(field, index, (val || []) as OrganizerBase[])"
            />
            <RecipeOrganizerSelector
              v-else-if="field.type === Organizer.Food"
              v-model="field.organizers"
              :selector-type="Organizer.Food"
              :show-add="false"
              :show-label="false"
              :show-icon="false"
              variant="underlined"
              @update:model-value="val => setFieldOrganizers(field, index, (val || []) as OrganizerBase[])"
            />
            <RecipeOrganizerSelector
              v-else-if="field.type === Organizer.Household"
              v-model="field.organizers"
              :selector-type="Organizer.Household"
              :show-add="false"
              :show-label="false"
              :show-icon="false"
              variant="underlined"
              @update:model-value="val => setFieldOrganizers(field, index, (val || []) as OrganizerBase[])"
            />
            <RecipeOrganizerSelector
              v-else-if="field.type === Organizer.User"
              v-model="field.organizers"
              :selector-type="Organizer.User"
              :show-add="false"
              :show-label="false"
              :show-icon="false"
              variant="underlined"
              @update:model-value="val => setFieldOrganizers(field, index, (val || []) as OrganizerBase[])"
            />
          </v-col>

          <!-- right parenthesis -->
          <v-col
            v-if="showAdvanced"
            :cols="config.items.rightParens.cols(index)"
            :sm="config.items.rightParens.sm(index)"
            :class="config.col.class"
          >
            <v-select
              :model-value="field.rightParenthesis"
              :items="['', ')', '))', ')))']"
              variant="underlined"
              @update:model-value="setRightParenthesisValue(field, index, $event)"
            >
              <template #chip="{ item }">
                <span :class="config.select.textClass" style="width: 100%;">
                  {{ item.raw }}
                </span>
              </template>
            </v-select>
          </v-col>

          <!-- field actions -->
          <v-col
            v-if="!$vuetify.display.smAndDown || index === fields.length - 1"
            :cols="config.items.fieldActions.cols(index)"
            :sm="config.items.fieldActions.sm(index)"
            :class="config.col.class"
          >
            <BaseButtonGroup
              :buttons="[
                {
                  icon: $globals.icons.delete,
                  text: $t('general.delete'),
                  event: 'delete',
                  disabled: fields.length === 1,
                },
              ]"
              class="my-auto"
              @delete="removeField(index)"
            />
          </v-col>
        </v-row>
      </VueDraggable>
    </v-card-text>
    <v-card-actions>
      <v-row fluid class="d-flex justify-end ma-2">
        <v-spacer />
        <v-checkbox
          v-model="showAdvanced"
          hide-details
          :label="$t('general.show-advanced')"
          class="my-auto mr-4"
          color="primary"
        />
        <BaseButton
          create
          :text="$t('general.add-field')"
          class="my-auto"
          @click="addField(fieldDefs[0])"
        />
      </v-row>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import { useDebounceFn } from "@vueuse/core";
import { useHouseholdSelf } from "~/composables/use-households";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import { Organizer } from "~/lib/api/types/non-generated";
import type {
  LogicalOperator,
  QueryFilterJSON,
  QueryFilterJSONPart,
  RelationalKeyword,
  RelationalOperator,
} from "~/lib/api/types/non-generated";
import { useCategoryStore, useFoodStore, useHouseholdStore, useTagStore, useToolStore } from "~/composables/store";
import { useUserStore } from "~/composables/store/use-user-store";
import { type Field, type FieldDefinition, type FieldValue, type OrganizerBase, useQueryFilterBuilder } from "~/composables/use-query-filter-builder";

const props = defineProps({
  fieldDefs: {
    type: Array as () => FieldDefinition[],
    required: true,
  },
  initialQueryFilter: {
    type: Object as () => QueryFilterJSON | null,
    default: null,
  },
});

const emit = defineEmits<{
  (event: "input", value: string | undefined): void;
  (event: "inputJSON", value: QueryFilterJSON | undefined): void;
}>();

const { household } = useHouseholdSelf();
const {
  logOps,
  placeholderKeywords,
  getRelOps,
  buildQueryFilterString,
  getFieldFromFieldDef,
  isOrganizerType,
} = useQueryFilterBuilder();

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

const state = reactive({
  showAdvanced: false,
  qfValid: false,
  datePickers: [] as boolean[],
  drag: false,
});
const { showAdvanced, datePickers, drag } = toRefs(state);

const storeMap = {
  [Organizer.Category]: useCategoryStore(),
  [Organizer.Tag]: useTagStore(),
  [Organizer.Tool]: useToolStore(),
  [Organizer.Food]: useFoodStore(),
  [Organizer.Household]: useHouseholdStore(),
  [Organizer.User]: useUserStore(),
};

function onDragEnd(event: any) {
  state.drag = false;

  const oldIndex: number = event.oldIndex;
  const newIndex: number = event.newIndex;
  state.datePickers[oldIndex] = false;
  state.datePickers[newIndex] = false;
}

// add id to fields to prevent reactivity issues
type FieldWithId = Field & { id: number };
const fields = ref<FieldWithId[]>([]);

const uid = ref(1); // init uid to pass to fields
function useUid() {
  return uid.value++;
}
function addField(field: FieldDefinition) {
  fields.value.push({
    ...getFieldFromFieldDef(field),
    id: useUid(),
  });
  state.datePickers.push(false);
}

function setField(index: number, fieldLabel: string) {
  state.datePickers[index] = false;
  const fieldDef = props.fieldDefs.find(fieldDef => fieldDef.label === fieldLabel);
  if (!fieldDef) {
    return;
  }

  const resetValue = (fieldDef.type !== fields.value[index].type) || (fieldDef.fieldChoices !== fields.value[index].fieldChoices);
  const updatedField = { ...fields.value[index], ...fieldDef };

  // we have to set this explicitly since it might be undefined
  updatedField.fieldChoices = fieldDef.fieldChoices;

  fields.value[index] = {
    ...getFieldFromFieldDef(updatedField, resetValue),
    id: fields.value[index].id, // keep the id
  };

  // Defaults
  switch (fields.value[index].type) {
    case "date":
      fields.value[index].value = safeNewDate("");
      break;
    case "relativeDate":
      fields.value[index].value = "$NOW-30d";
      break;

    default:
      break;
  }
}

function setLeftParenthesisValue(field: FieldWithId, index: number, value: string) {
  fields.value[index].leftParenthesis = value;
}

function setRightParenthesisValue(field: FieldWithId, index: number, value: string) {
  fields.value[index].rightParenthesis = value;
}

function setLogicalOperatorValue(field: FieldWithId, index: number, value: LogicalOperator | undefined) {
  if (!value) {
    value = logOps.value.AND.value;
  }

  fields.value[index].logicalOperator = value ? logOps.value[value] : undefined;
}

function setRelationalOperatorValue(field: FieldWithId, index: number, value: RelationalKeyword | RelationalOperator) {
  const relOps = getRelOps(field.type);
  fields.value[index].relationalOperatorValue = relOps.value[value];
}

function setFieldValue(field: FieldWithId, index: number, value: FieldValue) {
  state.datePickers[index] = false;

  if (field.type === "relativeDate") {
    // Value is set to an int representing the offset from $NOW
    // Values are assumed to be negative offsets ('-') with a unit of days ('d')
    fields.value[index].value = `$NOW-${Math.abs(value)}d`;
  }
  else {
    fields.value[index].value = value;
  }
}

function setFieldValues(field: FieldWithId, index: number, values: FieldValue[]) {
  fields.value[index].values = values;
}

function setFieldOrganizers(field: FieldWithId, index: number, organizers: OrganizerBase[]) {
  fields.value[index].organizers = organizers;
  // Sync the values array with the organizers array
  fields.value[index].values = organizers.map(org => org.id?.toString() || "").filter(id => id);
}

function removeField(index: number) {
  fields.value.splice(index, 1);
  state.datePickers.splice(index, 1);
}

const fieldsUpdater = useDebounceFn(() => {
  const qf = buildQueryFilterString(fields.value, state.showAdvanced);
  if (qf) {
    console.debug(`Set query filter: ${qf}`);
  }
  state.qfValid = !!qf;

  emit("input", qf || undefined);
  emit("inputJSON", qf ? buildQueryFilterJSON() : undefined);
}, 500);

watch(fields, fieldsUpdater, { deep: true });

async function hydrateOrganizers(field: FieldWithId, _index: number) {
  if (!field.values?.length || !isOrganizerType(field.type)) {
    return;
  }

  const { store, actions } = storeMap[field.type];
  if (!store.value.length) {
    await actions.refresh();
  }

  const organizers = field.values.map((value) => {
    const organizer = store.value.find(item => item?.id?.toString() === value);
    if (!organizer) {
      console.error(`Could not find organizer with id ${value}`);
      return undefined;
    }
    return organizer;
  });

  field.organizers = organizers.filter(organizer => organizer !== undefined) as OrganizerBase[];
  return field;
}

function initFieldsError(error = "") {
  if (error) {
    console.error(error);
  }

  fields.value = [];
  if (props.fieldDefs.length) {
    addField(props.fieldDefs[0]);
  }
}

async function initializeFields() {
  if (!props.initialQueryFilter?.parts?.length) {
    return initFieldsError();
  }

  const initFields: FieldWithId[] = [];
  let error = false;

  for (const [index, part] of props.initialQueryFilter.parts.entries()) {
    const fieldDef = props.fieldDefs.find(fieldDef => fieldDef.name === part.attributeName);
    if (!fieldDef) {
      error = true;
      return initFieldsError(`Invalid query filter; unknown attribute name "${part.attributeName || ""}"`);
    }

    const field: FieldWithId = {
      ...getFieldFromFieldDef(fieldDef),
      id: useUid(),
    };

    const relOps = getRelOps(field.type);

    field.leftParenthesis = part.leftParenthesis || field.leftParenthesis;
    field.rightParenthesis = part.rightParenthesis || field.rightParenthesis;
    field.logicalOperator = part.logicalOperator
      ? logOps.value[part.logicalOperator]
      : field.logicalOperator;
    field.relationalOperatorValue = part.relationalOperator
      ? relOps.value[part.relationalOperator]
      : field.relationalOperatorValue;
    field.relationalOperatorValue = part.relationalOperator
      ? relOps.value[part.relationalOperator]
      : field.relationalOperatorValue;

    if (field.leftParenthesis || field.rightParenthesis) {
      state.showAdvanced = true;
    }

    if (field.fieldChoices?.length || isOrganizerType(field.type)) {
      if (typeof part.value === "string") {
        field.values = part.value ? [part.value] : [];
      }
      else {
        field.values = part.value || [];
      }

      if (isOrganizerType(field.type)) {
        await hydrateOrganizers(field, index);
      }
    }
    else if (field.type === "boolean") {
      const boolString = part.value || "false";
      field.value = (
        boolString[0].toLowerCase() === "t"
        || boolString[0].toLowerCase() === "y"
        || boolString[0] === "1"
      );
    }
    else if (field.type === "number") {
      field.value = Number(part.value as string || "0");
      if (isNaN(field.value)) {
        error = true;
        return initFieldsError(`Invalid query filter; invalid number value "${(part.value || "").toString()}"`);
      }
    }
    else if (field.type === "date") {
      field.value = part.value as string || "";
      const date = new Date(field.value);
      if (isNaN(date.getTime())) {
        error = true;
        return initFieldsError(`Invalid query filter; invalid date value "${(part.value || "").toString()}"`);
      }
    }
    else {
      field.value = part.value as string || "";
    }

    initFields.push(field);
  }

  if (initFields.length && !error) {
    fields.value = initFields;
  }
  else {
    initFieldsError();
  }
}

onMounted(async () => {
  try {
    await initializeFields();
  }
  catch (error) {
    initFieldsError(`Error initializing fields: ${(error || "").toString()}`);
  }
});

function buildQueryFilterJSON(): QueryFilterJSON {
  const parts = fields.value.map((field) => {
    const part: QueryFilterJSONPart = {
      attributeName: field.name,
      leftParenthesis: field.leftParenthesis,
      rightParenthesis: field.rightParenthesis,
      logicalOperator: field.logicalOperator?.value,
      relationalOperator: field.relationalOperatorValue?.value,
    };

    if (field.fieldChoices?.length || isOrganizerType(field.type)) {
      part.value = field.values.map(value => value.toString());
    }
    else if (field.type === "boolean") {
      part.value = field.value ? "true" : "false";
    }
    else {
      part.value = (field.value || "").toString();
    }

    return part;
  });

  const qfJSON = { parts } as QueryFilterJSON;
  console.debug(`Built query filter JSON: ${JSON.stringify(qfJSON)}`);
  return qfJSON;
}

function safeNewDate(input: string): Date {
  const date = new Date(input);
  if (isNaN(date.getTime())) {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return today;
  }
  return date;
}

/**
 * Parse a relative date string offset (e.g. $NOW-30d --> 30)
 *
 * Currently only values with a negative offset ('-') and a unit of days ('d') are supported
 */
function parseRelativeDateOffset(value: string): number {
  const defaultVal = 30;
  if (!value) {
    return defaultVal;
  }

  try {
    if (!value.startsWith(placeholderKeywords.value["$NOW"].value)) {
      return defaultVal;
    }

    const remainder = value.slice(placeholderKeywords.value["$NOW"].value.length);
    if (!remainder.startsWith("-")) {
      throw new Error("Invalid operator (not '-')");
    }

    if (remainder.slice(-1) !== "d") {
      throw new Error("Invalid unit (not 'd')");
    }

    // Slice off sign and unit
    return parseInt(remainder.slice(1, -1));
  }
  catch (error) {
    console.warn(`Unable to parse relative date offset from '${value}': ${error}`);
    return defaultVal;
  }
}

const config = computed(() => {
  const multiple = fields.value.length > 1;
  const adv = state.showAdvanced;

  return {
    col: {
      class: "d-flex justify-center align-end py-0",
    },
    select: {
      textClass: "d-flex justify-center text-center",
    },
    items: {
      icon: {
        cols: (_index: number) => 2,
        sm: (_index: number) => 1,
        style: "width: fit-content;",
      },
      leftParens: {
        cols: (index: number) => (adv ? (index === 0 ? 2 : 0) : 0),
        sm: (_index: number) => (adv ? 1 : 0),
      },
      logicalOperator: {
        cols: (_index: number) => 0,
        sm: (_index: number) => (multiple ? 1 : 0),
      },
      fieldName: {
        cols: (index: number) => {
          if (adv) return index === 0 ? 8 : 12;
          return index === 0 ? 10 : 12;
        },
        sm: (_index: number) => (adv ? 2 : 3),
      },
      relationalOperator: {
        cols: (_index: number) => 12,
        sm: (_index: number) => 2,
      },
      fieldValue: {
        cols: (index: number) => {
          const last = index === fields.value.length - 1;
          if (adv) return last ? 8 : 10;
          return last ? 10 : 12;
        },
        sm: (_index: number) => (adv ? 3 : 4),
      },
      rightParens: {
        cols: (index: number) => (adv ? (index === fields.value.length - 1 ? 2 : 0) : 0),
        sm: (_index: number) => (adv ? 1 : 0),
      },
      fieldActions: {
        cols: (index: number) => (index === fields.value.length - 1 ? 2 : 0),
        sm: (_index: number) => 1,
      },
    },
  };
});
</script>

<style scoped>
* {
  font-size: 1em;
  --bg-opactity: calc(var(--v-hover-opacity) * var(--v-theme-overlay-multiplier));
}

.bg-dark {
  background-color: rgba(0, 0, 0, var(--bg-opactity));
}

.bg-light {
  background-color: rgba(255, 255, 255, var(--bg-opactity));
}

:deep(.date-input input) {
  text-align: end;
  padding-right: 6px;
}

:deep(.date-input .v-field__field) {
  align-items: center;
}
</style>
