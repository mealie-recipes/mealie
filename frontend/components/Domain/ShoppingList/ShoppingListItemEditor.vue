<template>
  <div>
    <v-card variant="outlined">
      <v-card-text class="pb-3 pt-1">
        <div class="d-md-flex align-center mb-2" style="gap: 20px">
          <div>
            <v-number-input
              v-model="listItem.quantity"
              hide-details
              :label="$t('form.quantity-label-abbreviated')"
              :min="0"
              :precision="null"
              variant="plain"
              control-variant="stacked"
              inset
              density="compact"
              class="centered-number-input"
              style="width: 100px;"
            />
          </div>
          <InputLabelType
            v-model="listItem.unit"
            v-model:item-id="listItem.unitId!"
            :items="units"
            :label="$t('recipe.unit')"
            :icon="$globals.icons.units"
            create
            @create="createAssignUnit"
          />
          <InputLabelType
            v-model="listItem.food"
            v-model:item-id="listItem.foodId!"
            :items="foods"
            :label="$t('shopping-list.food')"
            :icon="$globals.icons.foods"
            create
            @create="createAssignFood"
          />
        </div>
        <div class="d-md-flex align-center" style="gap: 20px">
          <v-textarea
            v-model="listItem.note"
            hide-details
            :label="$t('shopping-list.note')"
            rows="1"
            auto-grow
            autofocus
            @keypress="handleNoteKeyPress"
          />
        </div>
        <div class="d-flex flex-wrap align-end" style="gap: 20px">
          <div class="d-flex align-end">
            <div style="max-width: 300px" class="mt-3 mr-auto">
              <InputLabelType
                v-model="listItem.label"
                v-model:item-id="listItem.labelId!"
                :items="labels"
                :label="$t('shopping-list.label')"
                width="250"
              />
            </div>

            <v-menu
              v-if="listItem.recipeReferences && listItem.recipeReferences.length > 0"
              open-on-hover
              offset-y
              start
              top
            >
              <template #activator="{ props }">
                <v-icon class="mt-auto" :icon="$globals.icons.alert" v-bind="props" color="warning">
                  {{ $globals.icons.alert }}
                </v-icon>
              </template>
              <v-card max-width="350px" class="left-warning-border">
                <v-card-text>
                  {{ $t("shopping-list.linked-item-warning") }}
                </v-card-text>
              </v-card>
            </v-menu>
          </div>
          <BaseButton
            v-if="listItem.labelId && listItem.food && listItem.labelId !== listItem.food.labelId"
            small
            color="info"
            :icon="$globals.icons.tagArrowRight"
            :text="$t('shopping-list.save-label')"
            class="mt-2 align-items-flex-start"
            @click="assignLabelToFood"
          />
          <v-spacer />
        </div>
      </v-card-text>
      <v-card-actions class="ma-0 pt-0 pb-1 justify-end">
        <BaseButtonGroup
          :buttons="[
            ...(allowDelete
              ? [
                {
                  icon: $globals.icons.delete,
                  text: $t('general.delete'),
                  event: 'delete',
                },
              ]
              : []),
            {
              icon: $globals.icons.close,
              text: $t('general.cancel'),
              event: 'cancel',
            },
            {
              icon: $globals.icons.save,
              text: $t('general.save'),
              event: 'save',
            },
          ]"
          @save="$emit('save')"
          @cancel="$emit('cancel')"
          @delete="$emit('delete')"
        />
      </v-card-actions>
    </v-card>
  </div>
</template>

<script lang="ts">
import type { ShoppingListItemCreate, ShoppingListItemOut } from "~/lib/api/types/household";
import type { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";
import { useFoodStore, useFoodData, useUnitStore, useUnitData } from "~/composables/store";

export default defineNuxtComponent({
  props: {
    modelValue: {
      type: Object as () => ShoppingListItemCreate | ShoppingListItemOut,
      required: true,
    },
    labels: {
      type: Array as () => MultiPurposeLabelOut[],
      required: true,
    },
    units: {
      type: Array as () => IngredientUnit[],
      required: true,
    },
    foods: {
      type: Array as () => IngredientFood[],
      required: true,
    },
    allowDelete: {
      type: Boolean,
      required: false,
      default: true,
    },
  },
  emits: ["update:modelValue", "save", "cancel", "delete"],
  setup(props, context) {
    const foodStore = useFoodStore();
    const foodData = useFoodData();

    const unitStore = useUnitStore();
    const unitData = useUnitData();

    const listItem = computed({
      get: () => {
        return props.modelValue;
      },
      set: (val) => {
        context.emit("update:modelValue", val);
      },
    });

    watch(
      () => props.modelValue.quantity,
      () => {
        if (!props.modelValue.quantity) {
          listItem.value.quantity = 0;
        }
      },
    );

    watch(
      () => props.modelValue.food,
      (newFood) => {
        listItem.value.label = newFood?.label || null;
        listItem.value.labelId = listItem.value.label?.id || null;
      },
    );

    async function createAssignFood(val: string) {
      // keep UI reactive
      // eslint-disable-next-line @typescript-eslint/no-unused-expressions
      listItem.value.food ? (listItem.value.food.name = val) : (listItem.value.food = { name: val });

      foodData.data.name = val;
      const newFood = await foodStore.actions.createOne(foodData.data);
      if (newFood) {
        listItem.value.food = newFood;
        listItem.value.foodId = newFood.id;
      }
      foodData.reset();
    }

    async function createAssignUnit(val: string) {
      // keep UI reactive
      // eslint-disable-next-line @typescript-eslint/no-unused-expressions
      listItem.value.unit ? (listItem.value.unit.name = val) : (listItem.value.unit = { name: val });

      unitData.data.name = val;
      const newUnit = await unitStore.actions.createOne(unitData.data);
      if (newUnit) {
        listItem.value.unit = newUnit;
        listItem.value.unitId = newUnit.id;
      }
      unitData.reset();
    }

    async function assignLabelToFood() {
      if (!(listItem.value.food && listItem.value.foodId && listItem.value.labelId)) {
        return;
      }

      listItem.value.food.labelId = listItem.value.labelId;
      await foodStore.actions.updateOne(listItem.value.food);
    }

    return {
      listItem,
      createAssignFood,
      createAssignUnit,
      assignLabelToFood,
    };
  },
  methods: {
    handleNoteKeyPress(event) {
      // Save on Enter
      if (!event.shiftKey && event.key === "Enter") {
        event.preventDefault();
        this.$emit("save");
      }
    },
  },
});
</script>

<style scoped>
.centered-number-input :deep(.v-field) {
  display: flex;
  align-items: center;
}
</style>
