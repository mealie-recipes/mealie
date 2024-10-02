<template>
  <v-card>
    <v-card-text>
      <v-container>
        <v-row
          v-for="(field, index) in fields"
          :key="index"
        >
          <v-col cols="2">
            <v-select
              v-if="index"
              v-model="field.logicalOperator"
              :items="['AND', 'OR']"
              @input="setLogicalOperatorValue(field, index, $event)"
            >
              <template #selection="{ item }">
                <span class="d-flex justify-center" style="width: 100%;">
                  {{ item }}
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col cols="4">
            <v-select
              v-model="field.label"
              :items="fieldDefs"
              item-text="label"
              @change="setField(index, $event)"
            >
              <template #selection="{ item }">
                <span class="d-flex justify-center" style="width: 100%;">
                  {{ item.label }}
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col cols="2">
            <v-select
              v-if="field.type !== 'boolean'"
              v-model="field.relationalOperatorValue"
              :items="field.relationalOperatorOptions"
              @input="setRelationalOperatorValue(field, index, $event)"
            >
              <template #selection="{ item }">
                <span class="d-flex justify-center" style="width: 100%;">
                  {{ item }}
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col cols="4">
            <v-select
              v-if="field.fieldOptions"
              v-model="field.values"
              :items="field.fieldOptions"
              item-text="label"
              item-value="value"
              multiple
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
              @input="setFieldValue(field, index, $event)"
            />
            <v-date-picker
              v-else-if="field.type === 'Date'"
              v-model="field.value"
              no-title
              @input="setFieldValue(field, index, $event)"
            />
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-btn @click="addField(fieldDefs[0])">Add Field</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from "@nuxtjs/composition-api";

export type FieldType =
  | string
  | number
  | boolean
  | Date;

interface SelectableItem {
  label: string;
  value: FieldType;
};

export interface FieldDefinition {
  name: string;
  label: string;
  type: FieldType;
  fieldOptions?: SelectableItem[];
}

type LogicalOperator = "AND" | "OR";

interface Field extends FieldDefinition {
  logicalOperator: LogicalOperator | undefined;
  value: FieldType;
  values: FieldType[];
  relationalOperatorValue: string;
  relationalOperatorOptions: string[];
}

export default defineComponent({
  props: {
    fieldDefs: {
      type: Array as () => FieldDefinition[],
      required: true,
    },
  },
  setup(props, context) {
    function getFieldFromFieldDef(field: Field | FieldDefinition, resetValue = false): Field {
      const updatedField = {logicalOperator: "AND", ...field} as Field;
      let operatorOptions: string[];
      if (updatedField.fieldOptions?.length) {
        operatorOptions = [
          "IN",
          "NOT IN",
          "CONTAINS ALL",
        ];
        updatedField.value = "";
        updatedField.values = [];
      } else {
        switch (updatedField.type) {
          case "string":
            operatorOptions = [
              "=",
              "<>",
              "LIKE",
              "NOT LIKE",
            ];
            break;
          case "number":
            operatorOptions = [
              "=",
              "<>",
              ">",
              ">=",
              "<",
              "<=",
            ];
            break;
          case "boolean":
            operatorOptions = ["="];
            break;
          case "Date":
            operatorOptions = [
              "=",
              "<>",
              ">",
              ">=",
              "<",
              "<=",
            ];
            break;
          default:
            operatorOptions = ["=", "<>"];
        }
      }
      updatedField.relationalOperatorOptions = operatorOptions;
      if (!operatorOptions.includes(updatedField.relationalOperatorValue)) {
        updatedField.relationalOperatorValue = operatorOptions[0];
      }

      if (resetValue) {
        updatedField.value = "";
        updatedField.values = [];
      }

      return updatedField;
    };

    const fields = ref<Field[]>([]);

    function addField(field: FieldDefinition) {
      fields.value.push(getFieldFromFieldDef(field));
    };

    function setField(index: number, fieldLabel: string) {
      const fieldDef = props.fieldDefs.find((fieldDef) => fieldDef.label === fieldLabel);
      if (!fieldDef) {
        return;
      }

      const resetValue = fieldDef.type !== fields.value[index].type
      const updatedField = {...fields.value[index], ...fieldDef};
      fields.value.splice(index, 1, getFieldFromFieldDef(updatedField, resetValue));
    }

    function setLogicalOperatorValue(field: Field, index: number, value: LogicalOperator | undefined) {
      if (!index) {
        value = undefined;
      } else if (!value) {
        value = "AND";
      }

      fields.value.splice(index, 1, {
        ...field,
        logicalOperator: value,
      });
    }

    function setRelationalOperatorValue(field: Field, index: number, value: string) {
      fields.value.splice(index, 1, {
        ...field,
        relationalOperatorValue: value,
      });
    }

    function setFieldValue(field: Field, index: number, value: FieldType) {
      fields.value.splice(index, 1, {
        ...field,
        value: value,
      });
    }

    function removeField(index: number) {
      fields.value.splice(index, 1);
    };

    function buildQueryFilterString() {
      // TODO
      console.log(fields.value);
      return "";
    }

    watch(
      () => fields.value,
      (newFields) => {
        newFields.forEach((field, index) => {
          const updatedField = getFieldFromFieldDef(field);
          if (!index) {
            updatedField.logicalOperator = undefined;
          }

          fields.value[index] = updatedField;
          const qf = buildQueryFilterString();
          context.emit("input", qf);
        });
      },
      {
        deep: true
      },
    );

    if (props.fieldDefs.length) {
      addField(props.fieldDefs[0]);
    }

    return {
      fields,
      addField,
      setField,
      setLogicalOperatorValue,
      setRelationalOperatorValue,
      setFieldValue,
      removeField,
    };
  },
});
</script>
