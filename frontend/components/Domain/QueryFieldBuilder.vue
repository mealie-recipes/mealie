<template>
  <v-card>
    <v-card-text>
      <v-container>
        <v-row
          v-for="(field, index) in fields"
          :key="index"
        >
          <v-col :cols="attrs.fields.logicalOperator.cols">
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
          <v-col v-if="showAdvanced" :cols="attrs.fields.leftParens.cols">
            <v-select
              v-model="field.leftParenthesis"
              :items="['', '(', '((', '(((']"
              @input="setLeftParenthesisValue(field, index, $event)"
            >
              <template #selection="{ item }">
                <span class="d-flex justify-center" style="width: 100%;">
                  {{ item }}
                </span>
              </template>
            </v-select>
          </v-col>
          <v-col :cols="attrs.fields.fieldName.cols">
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
          <v-col :cols="attrs.fields.relationalOperator.cols">
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
          <v-col :cols="attrs.fields.fieldValue.cols">
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
            <v-date-picker
              v-else-if="field.type === 'Date'"
              v-model="field.value"
              no-title
              @input="setFieldValue(field, index, $event)"
            />
          </v-col>
          <v-col v-if="showAdvanced" :cols="attrs.fields.rightParens.cols">
            <v-select
              v-model="field.rightParenthesis"
              :items="['', ')', '))', ')))']"
              @input="setRightParenthesisValue(field, index, $event)"
            >
              <template #selection="{ item }">
                <span class="d-flex justify-center" style="width: 100%;">
                  {{ item }}
                </span>
              </template>
            </v-select>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
    <v-card-actions>
      <v-checkbox v-model="showAdvanced" label="Show Advanced" />
      <v-spacer />
      <v-btn @click="addField(fieldDefs[0])">Add Field</v-btn>
      <v-spacer />
      <span v-if="qfValid" class="green">QF Valid</span>
      <span v-else class="red">QF Not Valid</span>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, watch } from "@nuxtjs/composition-api";

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
  leftParenthesis: string | undefined;
  logicalOperator: LogicalOperator | undefined;
  value: FieldType;
  values: FieldType[];
  relationalOperatorValue: string;
  relationalOperatorOptions: string[];
  rightParenthesis: string | undefined;
}

export default defineComponent({
  props: {
    fieldDefs: {
      type: Array as () => FieldDefinition[],
      required: true,
    },
  },
  setup(props, context) {
    const state = reactive({
      showAdvanced: false,
      qfValid: false,
    });

    function getFieldFromFieldDef(field: Field | FieldDefinition, resetValue = false): Field {
      const updatedField = {logicalOperator: "AND", ...field} as Field;
      let operatorOptions: string[];
      if (updatedField.fieldOptions?.length) {
        operatorOptions = [
          "IN",
          "NOT IN",
          "CONTAINS ALL",
        ];
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

    function setFieldValues(field: Field, index: number, values: FieldType[]) {
      fields.value.splice(index, 1, {
        ...field,
        values: values,
      });
    }

    function removeField(index: number) {
      fields.value.splice(index, 1);
    };

    function buildQueryFilterString() {
      let isValid = true;
      let lParenCounter = 0;
      let rParenCounter = 0;

      const parts: string[] = [];
      fields.value.forEach((field, index) => {
        if (index) {
          if (field.logicalOperator) {
            parts.push(field.logicalOperator);
          } else {
            isValid = false;
          }
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
          parts.push(field.relationalOperatorValue);
        } else {
          if (field.type !== "boolean") {
            isValid = false;
          }
        }

        if (field.fieldOptions?.length) {
          if (field.values?.length) {
            let val: string;
            if (field.type === "string" || field.type === "Date") {
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
            if (field.type === "string" || field.type === "Date") {
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
        context.emit("input", qf || undefined);
      },
      {
        deep: true
      },
    );

    if (props.fieldDefs.length) {
      addField(props.fieldDefs[0]);
    }

    const attrs = computed(() => {
      const attrs = {
        fields: {
          leftParens: {
            cols: state.showAdvanced ? 1 : 0,
          },
          logicalOperator: {
            cols: 2,
          },
          fieldName: {
            cols: state.showAdvanced ? 2 : 3,
          },
          relationalOperator: {
            cols: 3,
          },
          fieldValue: {
            cols: state.showAdvanced ? 3 : 4,
          },
          rightParens: {
            cols: state.showAdvanced ? 1 : 0,
          },
        },
      }

      return attrs
    })

    return {
      ...toRefs(state),
      attrs,
      fields,
      addField,
      setField,
      setLeftParenthesisValue,
      setRightParenthesisValue,
      setLogicalOperatorValue,
      setRelationalOperatorValue,
      setFieldValue,
      setFieldValues,
      removeField,
    };
  },
});
</script>
