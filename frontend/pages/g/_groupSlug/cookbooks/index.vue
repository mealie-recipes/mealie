<template>
  <div>
    <!-- Delete Dialog -->
    <BaseDialog
      v-model="deleteDialog"
      :title="$tc('general.confirm')"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteCookbook()"
    >
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
        <p v-if="deleteTarget" class="mt-4 ml-4">{{ deleteTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Cookbook Page -->
    <!-- Page Title -->
    <v-container class="narrow-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
      </template>
      <template #title> {{ $t('cookbook.cookbooks') }} </template>
      {{ $t('cookbook.description') }}
    </BasePageTitle>

    <!-- Create New -->
    <BaseButton create @click="actions.createOne()" />

    <!-- Cookbook List -->
    <v-expansion-panels class="mt-2">
      <draggable v-model="cookbooks" handle=".handle" style="width: 100%" @change="actions.updateOrder()">
        <CookbookEditor
          :cookbooks="cookbooks"
          :actions="actions"
          @delete="deleteEventHandler"
        />
      </draggable>
    </v-expansion-panels>
  </v-container>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, useRouter } from "@nuxtjs/composition-api";
import draggable from "vuedraggable";
import { useCookbooks } from "@/composables/use-group-cookbooks";
import { useLoggedInState } from "~/composables/use-logged-in-state";
import CookbookEditor from "~/components/Domain/Cookbook/CookbookEditor.vue";
import { ReadCookBook } from "~/lib/api/types/cookbook";

export default defineComponent({
  components: { draggable, CookbookEditor },
  setup() {
    const { isOwnGroup, loggedIn } = useLoggedInState();
    const router = useRouter();


    if (!(loggedIn.value && isOwnGroup.value)) {
      router.back();
    }

    const { cookbooks, actions } = useCookbooks();

    // delete
    const deleteDialog = ref(false);
    const deleteTarget = ref<ReadCookBook | null>(null);
    function deleteEventHandler(item: ReadCookBook){
      deleteTarget.value = item;
      deleteDialog.value = true;
    }
    function deleteCookbook() {
      if (!deleteTarget.value) {
        return;
      }
      actions.deleteOne(deleteTarget.value.id);
      deleteDialog.value = false;
      deleteTarget.value = null;
    }


    return {
      cookbooks,
      actions,
      // delete
      deleteDialog,
      deleteTarget,
      deleteEventHandler,
      deleteCookbook,
    };
  },
  head() {
    return {
      title: this.$t("cookbook.cookbooks") as string,
    };
  },
});
</script>
