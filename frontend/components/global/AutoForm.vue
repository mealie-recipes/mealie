<template>
  <v-form v-model="isValid" validate-on="input">
    <v-card
      :color="color"
      :dark="dark"
      flat
      :width="width"
      class="my-2"
    >
      <v-row no-gutters>
        <template v-for="(inputField, index) in items" :key="index">
          <v-col
            v-if="inputField.section"
            :cols="12"
            class="px-2"
          >
            <v-divider
              class="my-2"
            />
            <v-card-title
              class="pl-0"
            >
              {{ inputField.section }}
            </v-card-title>
            <v-card-text
              v-if="inputField.sectionDetails"
              class="pl-0 mt-0 pt-0"
            >
              {{ inputField.sectionDetails }}
            </v-card-text>
          </v-col>
          <v-col
            :cols="inputField.cols || 12"
            class="px-2"
          >
            <!-- Check Box -->
            <v-checkbox
              v-if="inputField.type === fieldTypes.BOOLEAN"
              v-model="model[inputField.varName]"
              :name="inputField.varName"
              :readonly="fieldState[inputField.varName]?.readonly"
              :disabled="fieldState[inputField.varName]?.disabled"
              :hint="inputField.hint"
              :hide-details="!inputField.hint"
              :persistent-hint="!!inputField.hint"
              density="comfortable"
              validate-on="input"
            >
              <template #label>
                <span class="ml-4">
                  {{ inputField.label }}
                </span>
              </template>
            </v-checkbox>

            <!-- Text Field -->
            <v-text-field
              v-else-if="inputField.type === fieldTypes.TEXT || inputField.type === fieldTypes.PASSWORD"
              v-model="model[inputField.varName]"
              :readonly="fieldState[inputField.varName]?.readonly"
              :disabled="fieldState[inputField.varName]?.disabled"
              :type="inputField.type === fieldTypes.PASSWORD ? 'password' : 'text'"
              variant="solo-filled"
              flat
              density="comfortable"
              :label="inputField.label"
              :name="inputField.varName"
              :hint="inputField.hint || ''"
              :rules="!(inputField.disableUpdate && updateMode) ? inputField.rules || [] : []"
              validate-on="input"
            />

            <!-- Text Area -->
            <v-textarea
              v-else-if="inputField.type === fieldTypes.TEXT_AREA"
              v-model="model[inputField.varName]"
              :readonly="fieldState[inputField.varName]?.readonly"
              :disabled="fieldState[inputField.varName]?.disabled"
              variant="solo-filled"
              flat
              rows="3"
              auto-grow
              density="comfortable"
              :label="inputField.label"
              :name="inputField.varName"
              :hint="inputField.hint || ''"
              :rules="!(inputField.disableUpdate && updateMode) ? inputField.rules || [] : []"
              validate-on="input"
            />

            <!-- Number Input -->
            <v-number-input
              v-else-if="inputField.type === fieldTypes.NUMBER"
              v-model="model[inputField.varName]"
              variant="underlined"
              :control-variant="inputField.numberInputConfig?.controlVariant"
              density="comfortable"
              :label="inputField.label"
              :name="inputField.varName"
              :min="inputField.numberInputConfig?.min"
              :max="inputField.numberInputConfig?.max"
              :precision="inputField.numberInputConfig?.precision"
              :hint="inputField.hint"
              :hide-details="!inputField.hint"
              :persistent-hint="!!inputField.hint"
              :rules="!(inputField.disableUpdate && updateMode) ? inputField.rules || [] : []"
              validate-on="input"
            />

            <!-- Option Select -->
            <v-select
              v-else-if="inputField.type === fieldTypes.SELECT"
              v-model="model[inputField.varName]"
              :readonly="fieldState[inputField.varName]?.readonly"
              :disabled="fieldState[inputField.varName]?.disabled"
              variant="solo-filled"
              flat
              :label="inputField.label"
              :name="inputField.varName"
              :items="inputField.options"
              item-title="text"
              :item-value="inputField.selectReturnValue || 'text'"
              :return-object="false"
              :hint="inputField.hint"
              density="comfortable"
              persistent-hint
              :rules="!(inputField.disableUpdate && updateMode) ? inputField.rules || [] : []"
              validate-on="input"
            />

            <!-- Color Picker -->
            <div
              v-else-if="inputField.type === fieldTypes.COLOR"
              class="d-flex"
              style="width: 100%"
            >
              <InputColor v-model="model[inputField.varName]" />
            </div>
          </v-col>
        </template>
      </v-row>
    </v-card>
  </v-form>
</template>

<script lang="ts" setup>
import { fieldTypes } from "@/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";

// Use defineModel for v-model
const model = defineModel<Record<string, any> | any[]>({
  type: [Object, Array],
  required: true,
});
const isValid = defineModel("isValid", { type: Boolean, default: false });

const props = defineProps({
  updateMode: {
    default: false,
    type: Boolean,
  },
  items: {
    default: null,
    type: Array as () => AutoFormItems,
  },
  width: {
    type: [Number, String],
    default: "max",
  },
  color: {
    default: null,
    type: String,
  },
  dark: {
    default: false,
    type: Boolean,
  },
  disabledFields: {
    default: null,
    type: Array as () => string[],
  },
  readonlyFields: {
    default: null,
    type: Array as () => string[],
  },
});

// Combined state map for readonly and disabled fields
const fieldState = computed<Record<string, { readonly: boolean; disabled: boolean }>>(() => {
  const map: Record<string, { readonly: boolean; disabled: boolean }> = {};
  (props.items || []).forEach((field: any) => {
    const base = (field.disableUpdate && props.updateMode) || (!props.updateMode && field.disableCreate);
    map[field.varName] = {
      readonly: base || !!props.readonlyFields?.includes(field.varName),
      disabled: base || !!props.disabledFields?.includes(field.varName),
    };
  });
  return map;
});
</script>

<style lang="scss" scoped></style>
