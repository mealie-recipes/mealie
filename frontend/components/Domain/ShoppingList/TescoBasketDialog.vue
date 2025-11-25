<template>
  <BaseDialog
    v-model="dialog"
    title="Tesco Basket"
    :width="900"
  >
    <v-card-text>
      <div v-if="loading" class="text-center py-4">
        <v-progress-circular indeterminate color="primary" />
      </div>
      <div v-else-if="items.length === 0" class="text-center py-4">
        No Tesco products found in this shopping list.
      </div>
      <v-table v-else>
        <thead>
          <tr>
            <th>Product</th>
            <th>Quantity Needed</th>
            <th>Pack Size</th>
            <th>Packs to Buy</th>
            <th>Est. Cost</th>
            <th>Link</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.url">
            <td>{{ item.productName }}</td>
            <td>{{ item.totalQuantityNeeded.toFixed(2) }} {{ item.unit }}</td>
            <td>{{ item.packSize }} {{ item.unit }}</td>
            <td>{{ item.packsNeeded }}</td>
            <td>£{{ item.estimatedCost.toFixed(2) }}</td>
            <td>
              <v-btn
                :href="item.url"
                target="_blank"
                icon
                variant="text"
                color="primary"
              >
                <v-icon>{{ $globals.icons.openInNew }}</v-icon>
              </v-btn>
            </td>
          </tr>
        </tbody>
        <tfoot>
            <tr>
                <td colspan="4" class="text-right font-weight-bold">Total:</td>
                <td class="font-weight-bold">£{{ totalCost.toFixed(2) }}</td>
                <td></td>
            </tr>
        </tfoot>
      </v-table>
    </v-card-text>
    <v-card-actions>
      <v-btn
        variant="text"
        color="secondary"
        href="/scripts/tesco-basket-loader.user.js"
        target="_blank"
        prepend-icon="mdi-download"
      >
        Install Script
      </v-btn>
      <v-spacer />
      <BaseButton @click="dialog = false" variant="text" color="grey">Close</BaseButton>
      <BaseButton @click="shopAtTesco" color="primary" prepend-icon="mdi-cart-plus">Add to Tesco Basket</BaseButton>
    </v-card-actions>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import type { TescoBasketItem } from '~/lib/api/types/household';
import { useNuxtApp} from '#app';
import { useUserApi } from '~/composables/api';

const props = defineProps<{
  modelValue: boolean;
  shoppingListId: string;
}>();

const emit = defineEmits(['update:modelValue']);

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
});

const items = ref<TescoBasketItem[]>([]);
const loading = ref(false);
const { $globals } = useNuxtApp();
const api = useUserApi();

const totalCost = computed(() => items.value.reduce((acc, item) => acc + item.estimatedCost, 0));

const shopAtTesco = () => {
  const productIds = items.value
    .flatMap(item => {
      // Extract ID from URL: https://www.tesco.com/groceries/en-GB/products/305953125
      const match = item.url.match(/\/products\/(\d+)/);
      const id = match ? match[1] : null;
      
      if (id) {
        // Repeat the ID for each pack needed
        return Array(item.packsNeeded).fill(id);
      }
      return [];
    });

  if (productIds.length > 0) {
    const url = `https://www.tesco.com/groceries/en-GB/trolley#mealie_items=${productIds.join(',')}`;
    window.open(url, '_blank');
  }
};

watch(dialog, async (val) => {
  if (val) {
    loading.value = true;
    try {
      const { data } = await api.shopping.lists.getTescoBasket(props.shoppingListId);
      items.value = data || [];
    } catch (e) {
      console.error(e);
    } finally {
      loading.value = false;
    }
  }
});
</script>
