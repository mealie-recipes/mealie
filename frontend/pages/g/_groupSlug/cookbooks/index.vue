<template>
  <div>
    <!-- Create Dialog -->
    <BaseDialog
      v-if="createTarget"
      v-model="dialogStates.create"
      width="100%"
      max-width="1100px"
      :icon="$globals.icons.pages"
      :title="$t('cookbook.create-a-cookbook')"
      :submit-icon="$globals.icons.save"
      :submit-text="$tc('general.save')"
      :submit-disabled="!createTarget.queryFilterString"
      @submit="actions.updateOne(createTarget)"
      @cancel="deleteCreateTarget()"
    >
      <v-card-text>
        <CookbookEditor
          :key="createTargetKey"
          :cookbook=createTarget
          :actions="actions"
        />
      </v-card-text>
    </BaseDialog>

    <!-- Delete Dialog -->
    <BaseDialog
      v-model="dialogStates.delete"
      :title="$t('general.delete-with-name', { name: $t('cookbook.cookbook') })"
      :icon="$globals.icons.alertCircle"
      color="error"
      @confirm="deleteCookbook()"
    >
      <v-card-text>
        <p>{{ $t("general.confirm-delete-generic-with-name", { name: $t('cookbook.cookbook') }) }}</p>
        <p v-if="deleteTarget" class="mt-4 ml-4">{{ deleteTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Cookbook Page -->
    <!-- Page Title -->
    <v-container class="px-12">
      <BasePageTitle divider>
        <template #header>
          <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
        </template>
        <template #title> {{ $t('cookbook.cookbooks') }} </template>
        {{ $t('cookbook.description') }}
      </BasePageTitle>

      <div class="my-6">
        <v-checkbox
          v-model="cookbookPreferences.hideOtherHouseholds"
          :label="$tc('cookbook.hide-cookbooks-from-other-households')"
          hide-details
        />
        <div class="ml-8">
          <p class="text-subtitle-2 my-0 py-0">
            {{ $tc("cookbook.hide-cookbooks-from-other-households-description") }}
          </p>
        </div>
      </div>

      <!-- Create New -->
      <BaseButton create @click="createCookbook" />

      <!-- Cookbook List -->
      <v-expansion-panels class="mt-2">
        <draggable
          v-model="myCookbooks"
          handle=".handle"
          delay="250"
          :delay-on-touch-only="true"
          style="width: 100%"
          @change="actions.updateOrder(myCookbooks)"
        >
          <v-expansion-panel v-for="cookbook in myCookbooks" :key="cookbook.id" class="my-2 left-border rounded">
            <v-expansion-panel-header disable-icon-rotate class="headline">
              <div class="d-flex align-center">
                <v-icon large left>
                  {{ $globals.icons.pages }}
                </v-icon>
                {{ cookbook.name }}
              </div>
              <template #actions>
                <v-icon class="handle">
                  {{ $globals.icons.arrowUpDown }}
                </v-icon>
                <v-btn icon small class="ml-2">
                  <v-icon>
                    {{ $globals.icons.edit }}
                  </v-icon>
                </v-btn>
              </template>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <CookbookEditor :cookbook="cookbook" :actions="actions" :collapsable="false" @delete="deleteEventHandler" />
              <v-card-actions>
                <v-spacer></v-spacer>
                <BaseButtonGroup
                  :buttons="[{
                    icon: $globals.icons.delete,
                    text: $tc('general.delete'),
                    event: 'delete',
                  },
                  {
                    icon: $globals.icons.save,
                    text: $tc('general.save'),
                    event: 'save',
                    disabled: !cookbook.queryFilterString
                  },
                ]"
                @delete="deleteEventHandler(cookbook)"
                @save="actions.updateOne(cookbook)" />
              </v-card-actions>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </draggable>
      </v-expansion-panels>
    </v-container>
  </div>
</template>

<script lang="ts">

import { computed, defineComponent, onBeforeUnmount, onMounted, reactive, ref, useContext } from "@nuxtjs/composition-api";
import draggable from "vuedraggable";
import { useCookbooks } from "@/composables/use-group-cookbooks";
import { useHouseholdSelf } from "@/composables/use-households";
import CookbookEditor from "~/components/Domain/Cookbook/CookbookEditor.vue";
import { ReadCookBook } from "~/lib/api/types/cookbook";
import { useCookbookPreferences } from "~/composables/use-users/preferences";

export default defineComponent({
  components: { CookbookEditor, draggable },
  middleware: ["auth", "group-only"],
  setup() {
    const dialogStates = reactive({
      create: false,
      delete: false,
    });

    const { $auth, i18n } = useContext();
    const { cookbooks: allCookbooks, actions } = useCookbooks();
    const myCookbooks = computed<ReadCookBook[]>({
      get: () => {
        return allCookbooks.value?.filter((cookbook) => {
          return cookbook.householdId === $auth.user?.householdId;
        }) || [];
      },
      set: (value: ReadCookBook[]) => {
        actions.updateOrder(value);
      },
    });
    const { household } = useHouseholdSelf();
    const cookbookPreferences = useCookbookPreferences()

    // create
    const createTargetKey = ref(0);
    const createTarget = ref<ReadCookBook | null>(null);
    async function createCookbook() {
      const name = i18n.t("cookbook.household-cookbook-name", [household.value?.name || "", String((myCookbooks.value?.length ?? 0) + 1)]) as string
      await actions.createOne(name).then((cookbook) => {
        createTarget.value = cookbook as ReadCookBook;
        createTargetKey.value++;
      });
      dialogStates.create = true;
    }

    // delete
    const deleteTarget = ref<ReadCookBook | null>(null);
    function deleteEventHandler(item: ReadCookBook){
      deleteTarget.value = item;
      dialogStates.delete = true;
    }
    function deleteCookbook() {
      if (!deleteTarget.value) {
        return;
      }
      actions.deleteOne(deleteTarget.value.id);
      dialogStates.delete = false;
      deleteTarget.value = null;
    }

    function deleteCreateTarget() {
      if (!createTarget.value?.id) {
        return;
      }

      actions.deleteOne(createTarget.value.id);
      dialogStates.create = false;
      createTarget.value = null;
    }
    function handleUnmount() {
      if(!createTarget.value?.id || createTarget.value.queryFilterString) {
        return;
      }

      deleteCreateTarget();
    }
    onMounted(() => {
      window.addEventListener("beforeunload", handleUnmount);
    });
    onBeforeUnmount(() => {
      handleUnmount();
      window.removeEventListener("beforeunload", handleUnmount);
    });

    return {
      myCookbooks,
      cookbookPreferences,
      actions,
      dialogStates,
      // create
      createTargetKey,
      createTarget,
      createCookbook,

      // delete
      deleteTarget,
      deleteEventHandler,
      deleteCookbook,
      deleteCreateTarget,
    };
  },
  head() {
    return {
      title: this.$t("cookbook.cookbooks") as string,
    };
  },
});
</script>
