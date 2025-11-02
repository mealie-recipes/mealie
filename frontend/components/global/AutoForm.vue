<template>
  <v-card
    :color="color"
    :dark="dark"
    flat
    :width="width"
    class="my-2"
  >
    <v-row>
      <v-col
        v-for="(inputField, index) in items"
        :key="index"
        cols="12"
        sm="12"
      >
        <v-divider
          v-if="inputField.section"
          class="my-2"
        />
        <v-card-title
          v-if="inputField.section"
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
          @change="emitBlur"
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
          :autofocus="index === 0"
          density="comfortable"
          :label="inputField.label"
          :name="inputField.varName"
          :hint="inputField.hint || ''"
          :rules="!(inputField.disableUpdate && updateMode) ? [...rulesByKey(inputField.rules as any), ...defaultRules] : []"
          lazy-validation
          @blur="emitBlur"
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
          :rules="[...rulesByKey(inputField.rules as any), ...defaultRules]"
          lazy-validation
          @blur="emitBlur"
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
          item-value="text"
          :return-object="false"
          :hint="inputField.hint"
          density="comfortable"
          persistent-hint
          lazy-validation
          @blur="emitBlur"
        />

        <!-- Color Picker -->
        <div
          v-else-if="inputField.type === fieldTypes.COLOR"
          class="d-flex"
          style="width: 100%"
        >
          <v-menu offset-y>
            <template #activator="{ props: templateProps }">
              <v-btn
                class="my-2 ml-auto"
                style="min-width: 200px"
                :color="model[inputField.varName]"
                dark
                v-bind="templateProps"
              >
                {{ inputField.label }}
              </v-btn>
            </template>
            <v-color-picker
              v-model="model[inputField.varName]"
              value="#7417BE"
              hide-canvas
              hide-inputs
              show-swatches
              class="mx-auto"
              @input="emitBlur"
            />
          </v-menu>
        </div>

        <!-- Object Type -->
        <div v-else-if="inputField.type === fieldTypes.OBJECT">
          <auto-form
            v-model="model[inputField.varName]"
            :color="color"
            :items="(inputField as any).items"
            @blur="emitBlur"
          />
        </div>

        <!-- List Type -->
        <div v-else-if="inputField.type === fieldTypes.LIST">
          <div
            v-for="(item, idx) in model[inputField.varName]"
            :key="idx"
          >
            <p>
              {{ inputField.label }} {{ idx + 1 }}
              <span>
                <BaseButton
                  class="ml-5"
                  x-small
                  delete
                  @click="removeByIndex(model[inputField.varName], idx)"
                />
              </span>
            </p>
            <v-divider class="mb-5 mx-2" />
            <auto-form
              v-model="model[inputField.varName][idx]"
              :color="color"
              :items="(inputField as any).items"
              @blur="emitBlur"
            />
          </div>
          <v-card-actions>
            <v-spacer />
            <BaseButton
              small
              @click="model[inputField.varName].push(getTemplate((inputField as any).items))"
            >
              {{ $t("general.new") }}
            </BaseButton>
          </v-card-actions>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts" setup>
import { validators } from "@/composables/use-validators";
import { fieldTypes } from "@/composables/forms";
import type { AutoFormItems } from "~/types/auto-forms";

const BLUR_EVENT = "blur";

type ValidatorKey = keyof typeof validators;

// Use defineModel for v-model
const modelValue = defineModel<Record<string, any> | any[]>({
  type: [Object, Array],
  required: true,
});

// alias to avoid template TS complaining about possible undefined
const model = modelValue as any;

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
  globalRules: {
    default: null,
    type: Array as () => string[],
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

const emit = defineEmits(["blur", "update:modelValue"]);

function rulesByKey(keys?: ValidatorKey[] | null) {
  if (keys === undefined || keys === null) {
    return [] as any[];
  }

  const list: any[] = [];
  keys.forEach((key) => {
    const split = key.split(":");
    const validatorKey = split[0] as ValidatorKey;
    if (validatorKey in validators) {
      if (split.length === 1) {
        list.push((validators as any)[validatorKey]);
      }
      else {
        list.push((validators as any)[validatorKey](split[1] as any));
      }
    }
  });
  return list;
}

const defaultRules = computed<any[]>(() => rulesByKey(props.globalRules as any));

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

function removeByIndex(list: never[], index: number) {
  // Removes the item at the index
  list.splice(index, 1);
}

function getTemplate(item: AutoFormItems) {
  const obj = {} as { [key: string]: string };

  item.forEach((field) => {
    obj[field.varName] = "";
  });

  return obj;
}

function emitBlur() {
  emit(BLUR_EVENT, modelValue.value);
}
</script>

<style lang="scss" scoped></style>
