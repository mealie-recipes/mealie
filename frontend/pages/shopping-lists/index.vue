<template>
  <v-container v-if="shoppingLists" class="narrow-container">
    <BaseDialog v-model="createDialog" :title="$t('shopping-list.create-shopping-list')" @submit="createOne">
      <v-card-text>
        <v-text-field v-model="createName" autofocus :label="$t('shopping-list.new-list')"> </v-text-field>
      </v-card-text>
    </BaseDialog>

    <BaseDialog v-model="deleteDialog" :title="$t('general.confirm')" color="error" @confirm="deleteOne">
      <v-card-text> Are you sure you want to delete this item?</v-card-text>
    </BaseDialog>
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/shopping-cart.svg')"></v-img>
      </template>
      <template #title> Shopping Lists </template>
    </BasePageTitle>
    <BaseButton create @click="createDialog = true" />

    <section>
      <v-card v-for="list in shoppingLists" :key="list.id" class="my-2 left-border" :to="`/shopping-lists/${list.id}`">
        <v-card-title>
          <v-icon left>
            {{ $globals.icons.cartCheck }}
          </v-icon>
          {{ list.name }}
          <v-btn class="ml-auto" icon @click.prevent="openDelete(list.id)">
            <v-icon>
              {{ $globals.icons.delete }}
            </v-icon>
          </v-btn>
        </v-card-title>
      </v-card>
    </section>
    <div class="d-flex justify-end mt-10">
      <ButtonLink to="/shopping-lists/labels" text="Manage Labels" :icon="$globals.icons.tags" />
    </div>
  </v-container>
</template>
  
<script lang="ts">
import { defineComponent, useAsync, reactive, toRefs } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { useAsyncKey } from "~/composables/use-utils";

export default defineComponent({
  setup() {
    const userApi = useUserApi();

    const state = reactive({
      createName: "",
      createDialog: false,
      deleteDialog: false,
      deleteTarget: "",
    });

    const shoppingLists = useAsync(async () => {
      return await fetchShoppingLists();
    }, useAsyncKey());

    async function fetchShoppingLists() {
      const { data } = await userApi.shopping.lists.getAll();
      return data;
    }

    async function refresh() {
      shoppingLists.value = await fetchShoppingLists();
    }

    async function createOne() {
      const { data } = await userApi.shopping.lists.createOne({ name: state.createName });

      if (data) {
        refresh();
        state.createName = "";
      }
    }

    function openDelete(id: string) {
      state.deleteDialog = true;
      state.deleteTarget = id;
    }

    async function deleteOne() {
      const { data } = await userApi.shopping.lists.deleteOne(state.deleteTarget);
      if (data) {
        refresh();
      }
    }

    return {
      ...toRefs(state),
      shoppingLists,
      createOne,
      deleteOne,
      openDelete,
    };
  },
  head() {
    return {
      title: this.$t("shopping-list.shopping-list") as string,
    };
  },
});
</script>
