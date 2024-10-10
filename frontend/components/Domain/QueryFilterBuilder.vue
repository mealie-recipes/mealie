<template>
  <v-card class="ma-0" style="overflow-x: auto;">
    <v-card-text class="ma-0 pa-0">
      <v-container fluid class="ma-0 pa-0">
        <draggable
          :value="fields"
          handle=".handle"
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
            :key="index"
            class="d-flex flex-nowrap"
            style="max-width: 100%;"
          >
            <v-col
              :cols="attrs.fields.icon.cols"
              :class="attrs.col.class"
              :style="attrs.fields.icon.style"
            >
              <v-icon
                class="handle"
                style="width: 100%; height: 100%;"
              >
                {{ $globals.icons.arrowUpDown }}
              </v-icon>
            </v-col>
            <v-col
              :cols="attrs.fields.logicalOperator.cols"
              :class="attrs.col.class"
              :style="attrs.fields.logicalOperator.style"
            >
              <v-select
                v-if="index"
                v-model="field.logicalOperator"
                :items="[logOps.AND, logOps.OR]"
                item-text="label"
                item-value="value"
                @input="setLogicalOperatorValue(field, index, $event)"
              >
                <template #selection="{ item }">
                  <span :class="attrs.select.textClass" style="width: 100%;">
                    {{ item.label }}
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col
              v-if="showAdvanced"
              :cols="attrs.fields.leftParens.cols"
              :class="attrs.col.class"
              :style="attrs.fields.leftParens.style"
            >
              <v-select
                v-model="field.leftParenthesis"
                :items="['', '(', '((', '(((']"
                @input="setLeftParenthesisValue(field, index, $event)"
              >
                <template #selection="{ item }">
                  <span :class="attrs.select.textClass" style="width: 100%;">
                    {{ item }}
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col
              :cols="attrs.fields.fieldName.cols"
              :class="attrs.col.class"
              :style="attrs.fields.fieldName.style"
            >
              <v-select
                v-model="field.label"
                :items="fieldDefs"
                item-text="label"
                @change="setField(index, $event)"
              >
                <template #selection="{ item }">
                  <span :class="attrs.select.textClass" style="width: 100%;">
                    {{ item.label }}
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col
              :cols="attrs.fields.relationalOperator.cols"
              :class="attrs.col.class"
              :style="attrs.fields.relationalOperator.style"
            >
              <v-select
                v-if="field.type !== 'boolean'"
                v-model="field.relationalOperatorValue"
                :items="field.relationalOperatorOptions"
                item-text="label"
                item-value="value"
                @input="setRelationalOperatorValue(field, index, $event)"
              >
                <template #selection="{ item }">
                  <span :class="attrs.select.textClass" style="width: 100%;">
                    {{ item.label }}
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col
              :cols="attrs.fields.fieldValue.cols"
              :class="attrs.col.class"
              :style="attrs.fields.fieldValue.style"
            >
              <v-select
                v-if="field.fieldOptions"
                v-model="field.values"
                :items="field.fieldOptions"
                item-text="label"
                item-value="value"
                multiple
                @input="setFieldValues(field, index, $event)"
              />
              <v-text-field
                v-else-if="field.type === 'string'"
                v-model="field.value"
                @input="setFieldValue(field, index, $event)"
              />
              <v-text-field
                v-else-if="field.type === 'number'"
                type="number"
                v-model="field.value"
                @input="setFieldValue(field, index, $event)"
              />
              <v-checkbox
                v-else-if="field.type === 'boolean'"
                v-model="field.value"
                @change="setFieldValue(field, index, $event)"
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
                <template #activator="{ on, attrs }">
                  <v-text-field
                    v-model="field.value"
                    persistent-hint
                    :prepend-icon="$globals.icons.calendar"
                    v-bind="attrs"
                    readonly
                    v-on="on"
                  />
                </template>
                <v-date-picker
                  v-model="field.value"
                  no-title
                  :first-day-of-week="firstDayOfWeek"
                  :local="$i18n.locale"
                  @input="setFieldValue(field, index, $event)"
                />
              </v-menu>
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Category"
                v-model="field.organizers"
                :selector-type="Organizer.Category"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                @input="setOrganizerValues(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Tag"
                v-model="field.organizers"
                :selector-type="Organizer.Tag"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                @input="setOrganizerValues(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Tool"
                v-model="field.organizers"
                :selector-type="Organizer.Tool"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                @input="setOrganizerValues(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Food"
                v-model="field.organizers"
                :selector-type="Organizer.Food"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                @input="setOrganizerValues(field, index, $event)"
              />
              <RecipeOrganizerSelector
                v-else-if="field.type === Organizer.Household"
                v-model="field.organizers"
                :selector-type="Organizer.Household"
                :show-add="false"
                :show-label="false"
                :show-icon="false"
                @input="setOrganizerValues(field, index, $event)"
              />
            </v-col>
            <v-col
              v-if="showAdvanced"
              :cols="attrs.fields.rightParens.cols"
              :class="attrs.col.class"
              :style="attrs.fields.rightParens.style"
            >
              <v-select
                v-model="field.rightParenthesis"
                :items="['', ')', '))', ')))']"
                @input="setRightParenthesisValue(field, index, $event)"
              >
                <template #selection="{ item }">
                  <span :class="attrs.select.textClass" style="width: 100%;">
                    {{ item }}
                  </span>
                </template>
              </v-select>
            </v-col>
            <v-col
              :cols="attrs.fields.fieldActions.cols"
              :class="attrs.col.class"
              :style="attrs.fields.fieldActions.style"
            >
              <BaseButtonGroup
                :buttons="[
                  {
                    icon: $globals.icons.delete,
                    text: $tc('general.delete'),
                    event: 'delete',
                    disabled: fields.length === 1,
                  }
                ]"
                class="my-auto"
                @delete="removeField(index)"
              />
            </v-col>
          </v-row>
        </draggable>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-container fluid class="d-flex justify-end pa-0">
        <v-checkbox
          v-model="showAdvanced"
          hide-details
          :label="$tc('general.show-advanced')"
          class="my-auto mr-4"
        />
        <BaseButton create :text="$tc('general.add-field')" @click="addField(fieldDefs[0])" />
      </v-container>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import draggable from "vuedraggable";
import { computed, defineComponent, reactive, ref, toRefs, watch } from "@nuxtjs/composition-api";
import { useHouseholdSelf } from "~/composables/use-households";
import RecipeOrganizerSelector from "~/components/Domain/Recipe/RecipeOrganizerSelector.vue";
import { Organizer, RecipeOrganizer } from "~/lib/api/types/non-generated";
import { LogicalOperator, QueryFilterJSON, QueryFilterJSONPart, RelationalKeyword, RelationalOperator } from "~/lib/api/types/response";
import { useCategoryStore, useFoodStore, useHouseholdStore, useTagStore, useToolStore } from "~/composables/store";
import { FieldLogicalOperator, FieldRelationalOperator, useQueryFilterBuilder } from "~/composables/use-query-filter-builder";

interface OrganizerBase {
  id: string | number;
  name: string;
}

export type FieldType =
  | "string"
  | "number"
  | "boolean"
  | "date"
  | RecipeOrganizer;

export type FieldValue =
  | string
  | number
  | boolean
  | Date
  | Organizer;

interface SelectableItem {
  label: string;
  value: FieldValue;
};

export interface FieldDefinition {
  name: string;
  label: string;
  type: FieldType;

  // only for select/organizer fields
  fieldOptions?: SelectableItem[];
}

interface Field extends FieldDefinition {
  leftParenthesis?: string;
  logicalOperator?: FieldLogicalOperator;
  value: FieldValue;
  relationalOperatorValue: FieldRelationalOperator;
  relationalOperatorOptions: FieldRelationalOperator[];
  rightParenthesis?: string;

  // only for select/organizer fields
  values: FieldValue[];
  organizers: OrganizerBase[];
}

export default defineComponent({
  components: {
    draggable,
    RecipeOrganizerSelector,
  },
  props: {
    fieldDefs: {
      type: Array as () => FieldDefinition[],
      required: true,
    },
    initialQueryFilter: {
      type: Object as () => QueryFilterJSON | null,
      default: null,
    }
  },
  setup(props, context) {
    const { household } = useHouseholdSelf();
    const { logOps, relOps } = useQueryFilterBuilder();

    const firstDayOfWeek = computed(() => {
      return household.value?.preferences?.firstDayOfWeek || 0;
    });

    const state = reactive({
      showAdvanced: false,
      qfValid: false,
      datePickers: [] as boolean[],
      drag: false,
    });

    const storeMap = {
      [Organizer.Category]: useCategoryStore(),
      [Organizer.Tag]: useTagStore(),
      [Organizer.Tool]: useToolStore(),
      [Organizer.Food]: useFoodStore(),
      [Organizer.Household]: useHouseholdStore(),
    };

    function isOrganizerType(type: FieldType): type is Organizer {
      return (
        type === Organizer.Category ||
        type === Organizer.Tag ||
        type === Organizer.Tool ||
        type === Organizer.Food ||
        type === Organizer.Household
      );
    }

    function onDragEnd(event: any) {
      state.drag = false;

      const oldIndex: number = event.oldIndex;
      const newIndex: number = event.newIndex;
      state.datePickers[oldIndex] = false;
      state.datePickers[newIndex] = false;

      const field = fields.value.splice(oldIndex, 1)[0];
      fields.value.splice(newIndex, 0, field);
    }

    function getFieldFromFieldDef(field: Field | FieldDefinition, resetValue = false): Field {
      const updatedField = {logicalOperator: logOps.value.AND, ...field} as Field;
      let operatorOptions: FieldRelationalOperator[];
      if (updatedField.fieldOptions?.length || isOrganizerType(updatedField.type)) {
        operatorOptions = [
          relOps.value["IN"],
          relOps.value["NOT IN"],
          relOps.value["CONTAINS ALL"],
        ];
      } else {
        switch (updatedField.type) {
          case "string":
            operatorOptions = [
              relOps.value["="],
              relOps.value["<>"],
              relOps.value["LIKE"],
              relOps.value["NOT LIKE"],
            ];
            break;
          case "number":
            operatorOptions = [
              relOps.value["="],
              relOps.value["<>"],
              relOps.value[">"],
              relOps.value[">="],
              relOps.value["<"],
              relOps.value["<="],
            ];
            break;
          case "boolean":
            operatorOptions = [relOps.value["="]];
            break;
          case "date":
            operatorOptions = [
            relOps.value["="],
              relOps.value["<>"],
              relOps.value[">"],
              relOps.value[">="],
              relOps.value["<"],
              relOps.value["<="],
            ];
            break;
          default:
            operatorOptions = [relOps.value["="], relOps.value["<>"]];
        }
      }
      updatedField.relationalOperatorOptions = operatorOptions;
      if (!operatorOptions.includes(updatedField.relationalOperatorValue)) {
        updatedField.relationalOperatorValue = operatorOptions[0];
      }

      if (resetValue) {
        updatedField.value = "";
        updatedField.values = [];
        updatedField.organizers = [];
      } else {
        updatedField.value = updatedField.value || "";
        updatedField.values = updatedField.values || [];
        updatedField.organizers = updatedField.organizers || [];
      }


      return updatedField;
    };

    const fields = ref<Field[]>([]);

    function addField(field: FieldDefinition) {
      fields.value.push(getFieldFromFieldDef(field));
      state.datePickers.push(false);
    };

    function setField(index: number, fieldLabel: string) {
      state.datePickers[index] = false;
      const fieldDef = props.fieldDefs.find((fieldDef) => fieldDef.label === fieldLabel);
      if (!fieldDef) {
        return;
      }

      const resetValue = (fieldDef.type !== fields.value[index].type) || (fieldDef.fieldOptions !== fields.value[index].fieldOptions);
      const updatedField = {...fields.value[index], ...fieldDef};

      // we have to set this explicitly since it might be undefined
      updatedField.fieldOptions = fieldDef.fieldOptions;

      fields.value.splice(index, 1, getFieldFromFieldDef(updatedField, resetValue));
    }

    function setLeftParenthesisValue(field: Field, index: number, value: string) {
      fields.value.splice(index, 1, {
        ...field,
        leftParenthesis: value,
      });
    }

    function setRightParenthesisValue(field: Field, index: number, value: string) {
      fields.value.splice(index, 1, {
        ...field,
        rightParenthesis: value,
      });
    }

    function setLogicalOperatorValue(field: Field, index: number, value: LogicalOperator | undefined) {
      if (!index) {
        value = undefined;
      } else if (!value) {
        value = logOps.value.AND.value;
      }

      fields.value.splice(index, 1, {
        ...field,
        logicalOperator: value ? logOps.value[value] : undefined,
      });
    }

    function setRelationalOperatorValue(field: Field, index: number, value: RelationalKeyword | RelationalOperator) {
      fields.value.splice(index, 1, {
        ...field,
        relationalOperatorValue: relOps.value[value],
      });
    }

    function setFieldValue(field: Field, index: number, value: FieldValue) {
      state.datePickers[index] = false;
      fields.value.splice(index, 1, {
        ...field,
        value: value,
      });
    }

    function setFieldValues(field: Field, index: number, values: FieldValue[]) {
      fields.value.splice(index, 1, {
        ...field,
        values: values,
      });
    }

    function setOrganizerValues(field: Field, index: number, values: OrganizerBase[]) {
      setFieldValues(field, index, values.map((value) => value.id.toString()));
    }

    function removeField(index: number) {
      fields.value.splice(index, 1);
      state.datePickers.splice(index, 1);
    };

    function buildQueryFilterString() {
      let isValid = true;
      let lParenCounter = 0;
      let rParenCounter = 0;

      const parts: string[] = [];
      fields.value.forEach((field, index) => {
        if (index) {
          if (!field.logicalOperator) {
            field.logicalOperator = logOps.value.AND;
          }
          parts.push(field.logicalOperator.value);
        }

        if (field.leftParenthesis && state.showAdvanced) {
          lParenCounter += field.leftParenthesis.length;
          parts.push(field.leftParenthesis);
        }

        if (field.label) {
          parts.push(field.name);
        } else {
          isValid = false;
        }

        if (field.relationalOperatorValue) {
          parts.push(field.relationalOperatorValue.value);
        } else {
          if (field.type !== "boolean") {
            isValid = false;
          }
        }

        if (field.fieldOptions?.length || isOrganizerType(field.type)) {
          if (field.values?.length) {
            let val: string;
            if (field.type === "string" || field.type === "date" || isOrganizerType(field.type)) {
              val = field.values.map((value) => `"${value}"`).join(",");
            } else {
              val = field.values.join(",");
            }
            parts.push(`[${val}]`);
          } else {
            isValid = false;
          }
        } else {
          if (field.value) {
            if (field.type === "string" || field.type === "date") {
              parts.push(`"${field.value}"`);
            } else {
              parts.push(field.value.toString());
            }
          } else {
            if (field.type === "boolean") {
              parts.push("false");
            } else {
              isValid = false;
            }
          }
        }

        if (field.rightParenthesis && state.showAdvanced) {
          rParenCounter += field.rightParenthesis.length;
          parts.push(field.rightParenthesis);
        }
      });

      if (lParenCounter !== rParenCounter) {
        isValid = false;
      }

      state.qfValid = isValid;
      return isValid ? parts.join(" ") : "";
    }

    watch(
      // Toggling showAdvanced changes the builder logic without changing the field values,
      // so we need to manually trigger reactivity to re-run the builder.
      () => state.showAdvanced,
      () => {
        if (fields.value?.length) {
          fields.value = [...fields.value];
        }
      },
    )

    watch(
      () => fields.value,
      (newFields) => {
        newFields.forEach((field, index) => {
          const updatedField = getFieldFromFieldDef(field);

          // The first field shouldn't have a logical operator, but all other fields should.
          if (!index) {
            updatedField.logicalOperator = undefined;
          }

          fields.value[index] = updatedField;
        });

        const qf = buildQueryFilterString();
        if (qf) {
          console.debug(`Set query filter: ${qf}`);
        }

        context.emit("input", qf || undefined);
      },
      {
        deep: true
      },
    );

    async function hydrateOrganizers(field: Field, index: number) {
      if (!field.values?.length || !isOrganizerType(field.type)) {
        return;
      }

      field.organizers = [];

      const { store, actions } = storeMap[field.type];
      if (!store.value.length) {
        await actions.refresh();
      }

      const organizers = field.values.map((value) => store.value.find((organizer) => organizer.id === value));
      field.organizers = organizers.filter((organizer) => organizer !== undefined) as OrganizerBase[];
      setOrganizerValues(field, index, field.organizers);
    }

    function initFieldsError(error: string = "") {
      if (error) {
        console.error(error);
      }

      fields.value = [];
      if (props.fieldDefs.length) {
        addField(props.fieldDefs[0]);
      }
    }

    function initializeFields() {
      if (!props.initialQueryFilter?.parts?.length) {
        return initFieldsError();
      };

      const initFields: Field[] = [];
      let error = false;
      props.initialQueryFilter.parts.forEach((part: QueryFilterJSONPart, index: number) => {
        const fieldDef = props.fieldDefs.find((fieldDef) => fieldDef.name === part.attributeName);
        if (!fieldDef) {
          error = true;
          return initFieldsError(`"Invalid query filter; unknown attribute name "${part.attributeName}"`);
        }

        const field: Field = getFieldFromFieldDef(fieldDef);
        field.leftParenthesis = part.leftParenthesis || field.leftParenthesis;
        field.rightParenthesis = part.rightParenthesis || field.rightParenthesis;
        field.logicalOperator = part.logicalOperator ?
          logOps.value[part.logicalOperator] : field.logicalOperator;
        field.relationalOperatorValue = part.relationalOperator ?
          relOps.value[part.relationalOperator] : field.relationalOperatorValue;

        if (field.leftParenthesis || field.rightParenthesis) {
          state.showAdvanced = true;
        }

        if (field.fieldOptions?.length || isOrganizerType(field.type)) {
          if (typeof part.value === "string") {
            field.values = part.value ? [part.value] : [];
          } else {
            field.values = part.value || [];
          }

          if (isOrganizerType(field.type)) {
            hydrateOrganizers(field, index);
          }

        } else if (field.type === "boolean") {
          const boolString = part.value || "false";
          field.value = (
            boolString[0].toLowerCase() === "t" ||
            boolString[0].toLowerCase() === "y" ||
            boolString[0] === "1"
          );
        } else if (field.type === "number") {
          field.value = Number(part.value as string || "0");
          if (isNaN(field.value)) {
            error = true;
            return initFieldsError(`Invalid query filter; invalid number value "${part.value}"`);
          }
        } else if (field.type === "date") {
          field.value = part.value as string || "";
          const date = new Date(field.value);
          if (isNaN(date.getTime())) {
            error = true;
            return initFieldsError(`Invalid query filter; invalid date value "${part.value}"`);
          }
        } else {
          field.value = part.value as string || "";
        }

        initFields.push(field);
      });

      if (initFields.length && !error) {
        fields.value = initFields;
      } else {
        initFieldsError();
      }
    };

    try {
      initializeFields();
    } catch (error) {
      initFieldsError(`Error initializing fields: ${error}`);
    }


    const attrs = computed(() => {
      const baseColMaxWidth = 50;
      const attrs = {
        col: {
          class: "d-flex justify-center align-end field-col pa-1",
        },
        select: {
          textClass: "d-flex justify-center text-center",
        },
        fields: {
          icon: {
            cols: 1,
            style: `width: fit-content;`,
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
            cols: state.showAdvanced ? 2 : 3,
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
      }

      return attrs
    })

    return {
      Organizer,
      ...toRefs(state),
      logOps,
      relOps,
      attrs,
      firstDayOfWeek,
      onDragEnd,
      // Fields
      fields,
      addField,
      setField,
      setLeftParenthesisValue,
      setRightParenthesisValue,
      setLogicalOperatorValue,
      setRelationalOperatorValue,
      setFieldValue,
      setFieldValues,
      setOrganizerValues,
      removeField,
    };
  },
});
</script>

<style scoped>
* {
  font-size: 1em;
}
</style>
