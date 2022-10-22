<template>
  <div>
    <v-card outlined>
      <v-card-text class="pb-3 pt-1">
        <div v-if="listItem.isFood" class="d-md-flex align-center mb-2" style="gap: 20px">
          <InputLabelType
            v-model="listItem.food"
            :items="foods"
            :item-id.sync="listItem.foodId"
            :label="$t('shopping-list.food')"
            :icon="$globals.icons.foods"
          />
          <InputLabelType
            v-model="listItem.unit"
            :items="units"
            :item-id.sync="listItem.unitId"
            :label="$t('general.units')"
            :icon="$globals.icons.units"
          />
        </div>
        <div class="d-md-flex align-center" style="gap: 20px">
          <v-textarea
            v-model="listItem.note"
            hide-details
            :label="$t('shopping-list.note')"
            rows="1"
            auto-grow
          ></v-textarea>
        </div>
        <div class="d-flex align-end" style="gap: 20px">
          <div>
            <InputQuantity v-model="listItem.quantity" />
          </div>
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
      </v-card-text>
    </v-card>
    <v-card-actions class="ma-0 pt-0 pb-1 justify-end">
      <BaseButtonGroup
        :buttons="[
          {
            icon: $globals.icons.delete,
            text: $t('general.delete'),
            event: 'delete',
          },
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
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from "@nuxtjs/composition-api";
import { ShoppingListItemCreate, ShoppingListItemOut } from "~/lib/api/types/group";
import { MultiPurposeLabelOut } from "~/lib/api/types/labels";
import { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";

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
  },
  setup(props, context) {
    const listItem = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });
    return {
      listItem,
    };
  },
});
</script>
