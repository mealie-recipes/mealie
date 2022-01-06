<template>
  <v-card :color="color" :dark="dark" flat :width="width" class="my-2">
    <v-row>
      <v-col v-for="(inputField, index) in items" :key="index" class="py-0" cols="12" sm="12">
        <v-divider v-if="inputField.section" class="my-2" />
        <v-card-title v-if="inputField.section" class="pl-0">
          {{ inputField.section }}
        </v-card-title>
        <v-card-text v-if="inputField.sectionDetails" class="pl-0 mt-0 pt-0">
          {{ inputField.sectionDetails }}
        </v-card-text>

        <!-- Check Box -->
        <v-checkbox
          v-if="inputField.type === fieldTypes.BOOLEAN"
          v-model="value[inputField.varName]"
          class="my-0 py-0"
          :label="inputField.label"
          :name="inputField.varName"
          :hint="inputField.hint || ''"
          :disabled="updateMode && inputField.disableUpdate"
          @change="emitBlur"
        />

        <!-- Text Field -->
        <v-text-field
          v-else-if="inputField.type === fieldTypes.TEXT || inputField.type === fieldTypes.PASSWORD"
          v-model="value[inputField.varName]"
          :readonly="inputField.disableUpdate && updateMode"
          :disabled="inputField.disableUpdate && updateMode"
          filled
          :type="inputField.type === fieldTypes.PASSWORD ? 'password' : 'text'"
          rounded
          class="rounded-lg"
          :autofocus="index === 0"
          dense
          :label="inputField.label"
          :name="inputField.varName"
          :hint="inputField.hint || ''"
          :rules="!(inputField.disableUpdate && updateMode) ? [...rulesByKey(inputField.rules), ...defaultRules] : []"
          lazy-validation
          @blur="emitBlur"
        />

        <!-- Text Area -->
        <v-textarea
          v-else-if="inputField.type === fieldTypes.TEXT_AREA"
          v-model="value[inputField.varName]"
          :readonly="inputField.disableUpdate && updateMode"
          :disabled="inputField.disableUpdate && updateMode"
          filled
          rounded
          class="rounded-lg"
          rows="3"
          auto-grow
          dense
          :label="inputField.label"
          :name="inputField.varName"
          :hint="inputField.hint || ''"
          :rules="[...rulesByKey(inputField.rules), ...defaultRules]"
          lazy-validation
          @blur="emitBlur"
        />

        <!-- Option Select -->
        <v-select
          v-else-if="inputField.type === fieldTypes.SELECT"
          v-model="value[inputField.varName]"
          :readonly="inputField.disableUpdate && updateMode"
          filled
          rounded
          class="rounded-lg"
          :prepend-icon="inputField.icons ? value[inputField.varName] : null"
          :label="inputField.label"
          :name="inputField.varName"
          :items="inputField.options"
          :return-object="false"
          lazy-validation
          @blur="emitBlur"
        >
          <template #item="{ item }">
            <v-list-item-content>
              <v-list-item-title>{{ item.text }}</v-list-item-title>
              <v-list-item-subtitle>{{ item.description }}</v-list-item-subtitle>
            </v-list-item-content>
          </template>
        </v-select>

        <!-- Color Picker -->
        <div v-else-if="inputField.type === fieldTypes.COLOR" class="d-flex" style="width: 100%">
          <v-menu offset-y>
            <template #activator="{ on }">
              <v-btn class="my-2 ml-auto" style="min-width: 200px" :color="value[inputField.varName]" dark v-on="on">
                {{ inputField.label }}
              </v-btn>
            </template>
            <v-color-picker
              v-model="value[inputField.varName]"
              value="#7417BE"
              hide-canvas
              hide-inputs
              show-swatches
              class="mx-auto"
              @input="emitBlur"
            />
          </v-menu>
        </div>

        <div v-else-if="inputField.type === fieldTypes.OBJECT">
          <auto-form v-model="value[inputField.varName]" :color="color" :items="inputField.items" @blur="emitBlur" />
        </div>

        <!-- List Type -->
        <div v-else-if="inputField.type === fieldTypes.LIST">
          <div v-for="(item, idx) in value[inputField.varName]" :key="idx">
            <p>
              {{ inputField.label }} {{ idx + 1 }}
              <span>
                <BaseButton class="ml-5" x-small delete @click="removeByIndex(value[inputField.varName], idx)" />
              </span>
            </p>
            <v-divider class="mb-5 mx-2" />
            <auto-form
              v-model="value[inputField.varName][idx]"
              :color="color"
              :items="inputField.items"
              @blur="emitBlur"
            />
          </div>
          <v-card-actions>
            <v-spacer />
            <BaseButton small @click="value[inputField.varName].push(getTemplate(inputField.items))"> New </BaseButton>
          </v-card-actions>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<script lang="ts">
import { computed, defineComponent } from "@nuxtjs/composition-api";
import { validators } from "@/composables/use-validators";
import { fieldTypes } from "@/composables/forms";
import { AutoFormItems } from "~/types/auto-forms";

const BLUR_EVENT = "blur";

export default defineComponent({
  name: "AutoForm",
  props: {
    value: {
      default: null,
      type: [Object, Array],
    },
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
  },
  setup(props, context) {
    function rulesByKey(keys?: string[] | null) {
      if (keys === undefined || keys === null) {
        return [];
      }

      const list = [] as ((v: string) => (boolean | string))[];
      keys.forEach((key) => {
        if (key in validators) {
          list.push(validators[key]);
        }
      });
      return list;
    }

    const defaultRules = computed(() => rulesByKey(props.globalRules));

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
      context.emit(BLUR_EVENT, props.value);
    }

    return {
      rulesByKey,
      defaultRules,
      removeByIndex,
      getTemplate,
      emitBlur,
      fieldTypes,
      validators,
    };
  },
});
</script>

<style lang="scss" scoped></style>
