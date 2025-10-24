<template>
  <v-card class="ma-0" style="overflow-x: auto;">
    <v-card-text class="ma-0 pa-0">
      <v-container fluid class="ma-0 pa-0">
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
            class="d-flex flex-nowrap"
            style="max-width: 100%;"
          >
            <!-- drag handle -->
            <v-col
              :cols="config.items.icon.cols"
              :class="config.col.class"
              :style="config.items.icon.style"
            >
              <v-icon
                class="handle"
                :size="24"
                style="cursor: move;margin: auto;"
              >
                {{ $globals.icons.arrowUpDown }}
              </v-icon>
            </v-col>
            <!-- and / or  -->
            <v-col
              :cols="config.items.logicalOperator.cols"
              :class="config.col.class"
              :style="config.items.logicalOperator.style"
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
              :cols="config.items.leftParens.cols"
              :class="config.col.class"
              :style="config.items.leftParens.style"
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
              :cols="config.items.fieldName.cols"
              :class="config.col.class"
              :style="config.items.fieldName.style"
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
              :cols="config.items.relationalOperator.cols"
              :class="config.col.class"
              :style="config.items.relationalOperator.style"
            >
              <v-select
                v-if="field.type !== 'boolean'"
                :model-value="field.relationalOperatorValue"
                :items="field.relationalOperatorOptions"
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
              :cols="config.items.fieldValue.cols"
              :class="config.col.class"
              :style="config.items.fieldValue.style"
            >
              <v-select
                v-if="field.fieldOptions"
                :model-value="field.values"
                :items="field.fieldOptions"
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
              <v-text-field
                v-else-if="field.type === 'number'"
                :model-value="field.value"
                type="number"
                variant="underlined"
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
                    v-model="field.value"
                    persistent-hint
                    :prepend-icon="$globals.icons.calendar"
                    variant="underlined"
                    color="primary"
                    v-bind="activatorProps"
                    readonly
                  />
                </template>
                <v-date-picker
                  :model-value="field.value ? new Date(field.value + 'T00:00:00') : null"
                  hide-header
                  :first-day-of-week="firstDayOfWeek"
                  :local="$i18n.locale"
                  @update:model-value="val => setFieldValue(field, index, val ? val.toISOString().slice(0, 10) : '')"
                />
              </v-menu>
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Category"
                v-model="field.organizers"
                :selector-type="Organizer.Category"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                variant="underlined"
                @update:model-value="setFieldOrganizers(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Tag"
                v-model="field.organizers"
                :selector-type="Organizer.Tag"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                variant="underlined"
                @update:model-value="setFieldOrganizers(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Tool"
                v-model="field.organizers"
                :selector-type="Organizer.Tool"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                variant="underlined"
                @update:model-value="setFieldOrganizers(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Food"
                v-model="field.organizers"
                :selector-type="Organizer.Food"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                variant="underlined"
                @update:model-value="setFieldOrganizers(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Household"
                v-model="field.organizers"
                :selector-type="Organizer.Household"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                variant="underlined"
                @update:model-value="setFieldOrganizers(field, index, $event)"
              />
            </v-col>
            <!-- right parenthesis -->
            <v-col
              v-if="showAdvanced"
              :cols="config.items.rightParens.cols"
              :class="config.col.class"
              :style="config.items.rightParens.style"
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
              :cols="config.items.fieldActions.cols"
              :class="config.col.class"
              :style="config.items.fieldActions.style"
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
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-row fluid class="d-flex justify-end pa-0 mx-2">
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
import type { LogicalOperator, QueryFilterJSON, QueryFilterJSONPart, RelationalKeyword, RelationalOperator } from "~/lib/api/types/response";
import { useCategoryStore, useFoodStore, useHouseholdStore, useTagStore, useToolStore } from "~/composables/store";
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
const { logOps, relOps, buildQueryFilterString, getFieldFromFieldDef, isOrganizerType } = useQueryFilterBuilder();

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

  const resetValue = (fieldDef.type !== fields.value[index].type) || (fieldDef.fieldOptions !== fields.value[index].fieldOptions);
  const updatedField = { ...fields.value[index], ...fieldDef };

  // we have to set this explicitly since it might be undefined
  updatedField.fieldOptions = fieldDef.fieldOptions;

  fields.value[index] = {
    ...getFieldFromFieldDef(updatedField, resetValue),
    id: fields.value[index].id, // keep the id
  };
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
  fields.value[index].relationalOperatorValue = relOps.value[value];
}

function setFieldValue(field: FieldWithId, index: number, value: FieldValue) {
  state.datePickers[index] = false;
  fields.value[index].value = value;
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

const fieldsUpdater = useDebounceFn((/* newFields: typeof fields.value */) => {
  /* newFields.forEach((field, index) => {
    const updatedField = getFieldFromFieldDef(field);
    fields.value[index] = updatedField; // recursive!!!
  }); */

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
    field.leftParenthesis = part.leftParenthesis || field.leftParenthesis;
    field.rightParenthesis = part.rightParenthesis || field.rightParenthesis;
    field.logicalOperator = part.logicalOperator
      ? logOps.value[part.logicalOperator]
      : field.logicalOperator;
    field.relationalOperatorValue = part.relationalOperator
      ? relOps.value[part.relationalOperator]
      : field.relationalOperatorValue;

    if (field.leftParenthesis || field.rightParenthesis) {
      state.showAdvanced = true;
    }

    if (field.fieldOptions?.length || isOrganizerType(field.type)) {
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

    if (field.fieldOptions?.length || isOrganizerType(field.type)) {
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

const config = computed(() => {
  const baseColMaxWidth = 55;
  return {
    col: {
      class: "d-flex justify-center align-end field-col pa-1",
    },
    select: {
      textClass: "d-flex justify-center text-center",
    },
    items: {
      icon: {
        cols: 1,
        style: "width: fit-content;",
      },
      leftParens: {
        cols: state.showAdvanced ? 1 : 0,
        style: `min-width: ${state.showAdvanced ? baseColMaxWidth : 0}px;`,
      },
      logicalOperator: {
        cols: 1,
        style: `min-width: ${baseColMaxWidth}px;`,
      },
      fieldName: {
        cols: state.showAdvanced ? 2 : 3,
        style: `min-width: ${state.showAdvanced ? baseColMaxWidth * 2 : baseColMaxWidth * 3}px;`,
      },
      relationalOperator: {
        cols: 2,
        style: `min-width: ${baseColMaxWidth * 2}px;`,
      },
      fieldValue: {
        cols: state.showAdvanced ? 3 : 4,
        style: `min-width: ${state.showAdvanced ? baseColMaxWidth * 2 : baseColMaxWidth * 3}px;`,
      },
      rightParens: {
        cols: state.showAdvanced ? 1 : 0,
        style: `min-width: ${state.showAdvanced ? baseColMaxWidth : 0}px;`,
      },
      fieldActions: {
        cols: 1,
        style: `min-width: ${baseColMaxWidth}px;`,
      },
    },
  };
});
</script>

<style scoped>
* {
  font-size: 1em;
}
</style>
