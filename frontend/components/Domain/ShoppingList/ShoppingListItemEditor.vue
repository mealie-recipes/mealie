<template>
  <div>
    <v-card outlined>
      <v-card-text class="pb-3 pt-1">
        <div v-if="listItem.isFood" class="d-md-flex align-center mb-2" style="gap: 20px">
          <div>
            <InputQuantity v-model="listItem.quantity" />
          </div>
          <InputLabelType
            v-model="listItem.unit"
            :items="units"
            :item-id.sync="listItem.unitId"
            :label="$t('general.units')"
            :icon="$globals.icons.units"
            @create="createAssignUnit"
          />
          <InputLabelType
            v-model="listItem.food"
            :items="foods"
            :item-id.sync="listItem.foodId"
            :label="$t('shopping-list.food')"
            :icon="$globals.icons.foods"
            @create="createAssignFood"
          />

        </div>
        <div class="d-md-flex align-center" style="gap: 20px">
          <div v-if="!listItem.isFood">
              <InputQuantity v-model="listItem.quantity" />
            </div>
          <v-textarea
            v-model="listItem.note"
            hide-details
            :label="$t('shopping-list.note')"
            rows="1"
            auto-grow
            autofocus
            @keypress="handleNoteKeyPress"
          ></v-textarea>
        </div>
        <div class="d-flex flex-wrap align-end" style="gap: 20px">
          <div class="d-flex align-end">

            <div style="max-width: 300px" class="mt-3 mr-auto">
              <InputLabelType
                v-model="listItem.label"
                :items="labels"
                :item-id.sync="listItem.labelId"
                :label="$t('shopping-list.label')"
              />
            </div>

            <v-menu
              v-if="listItem.recipeReferences && listItem.recipeReferences.length > 0"
              open-on-hover
              offset-y
              left
              top
            >
              <template #activator="{ on, attrs }">
                <v-icon class="mt-auto" icon v-bind="attrs" color="warning" v-on="on">
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
            :text="$tc('shopping-list.save-label')"
            class="mt-2 align-items-flex-start"
            @click="assignLabelToFood"
          />
          <v-spacer />
        </div>
      </v-card-text>
      <v-card-actions class="ma-0 pt-0 pb-1 justify-end">
        <BaseButtonGroup
          :buttons="[
            ...(allowDelete ? [{
              icon: $globals.icons.delete,
              text: $t('general.delete'),
              event: 'delete',
            }] : []),
            {
              icon: $globals.icons.close,
              text: $t('general.cancel'),
              event: 'cancel',
            },
            {
              icon: $globals.icons.foods,
              text: $t('shopping-list.toggle-food'),
              event: 'toggle-foods',
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
          @toggle-foods="listItem.isFood = !listItem.isFood"
        />
      </v-card-actions>
    </v-card>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, watch } from "@nuxtjs/composition-api";
import { ShoppingListItemCreate, ShoppingListItemOut } from "~/lib/api/types/household";
import { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";
import { useFoodStore, useFoodData, useUnitStore, useUnitData } from "~/composables/store";

export default defineComponent({
  props: {
    value: {
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
  setup(props, context) {
    const foodStore = useFoodStore();
    const foodData = useFoodData();

    const unitStore = useUnitStore();
    const unitData = useUnitData();

    const listItem = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    watch(
      () => props.value.food,
      (newFood) => {
        // @ts-ignore our logic already assumes there's a label attribute, even if TS doesn't think there is
        listItem.value.label = newFood?.label || null;
        listItem.value.labelId = listItem.value.label?.id || null;
      }
    );

    async function createAssignFood(val: string) {
      // keep UI reactive
      listItem.value.food ? listItem.value.food.name = val : listItem.value.food = { name: val };

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
      listItem.value.unit ? listItem.value.unit.name = val : listItem.value.unit = { name: val };

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
      // @ts-ignore the food will have an id, even though TS says it might not
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
  }
});
</script>
