<template>
  <BaseDialog
    v-model="model"
    bottom-sheet
    :title="$t('shopping-list.create-shopping-list')"
    :icon="$globals.icons.formatListCheck"
    can-submit
    :loading="loading"
    @submit="async () => {
      loading = true;
      await createOne().finally(() => loading = false);
      $emit('submit');
    }"
  >
    <v-card-text>
      <v-text-field
        v-model="state.createName"
        autofocus
        :label="$t('shopping-list.new-list')"
      />
    </v-card-text>
  </BaseDialog>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";

const model = defineModel<boolean>({ default: false });
defineEmits<{
  submit: [];
}>();

const state = reactive({
  createName: "",
});
const userApi = useUserApi();
const loading = ref<boolean>(false);

async function createOne() {
  const { data } = await userApi.shopping.lists.createOne({ name: state.createName });

  if (data) {
    state.createName = "";
  }
}
</script>
