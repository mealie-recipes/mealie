<template>
  <v-container
    v-if="shoppingList"
    class="md-container"
  >
    <BaseDialog
      v-model="state.checkAllDialog"
      :title="$t('general.confirm')"
      can-confirm
      @confirm="checkAll"
    >
      <v-card-text>
        {{ $t('shopping-list.are-you-sure-you-want-to-check-all-items') }}
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="state.uncheckAllDialog"
      :title="$t('general.confirm')"
      can-confirm
      @confirm="uncheckAll"
    >
      <v-card-text>
        {{ $t('shopping-list.are-you-sure-you-want-to-uncheck-all-items') }}
      </v-card-text>
    </BaseDialog>

    <BaseDialog
      v-model="state.deleteCheckedDialog"
      :title="$t('general.confirm')"
      can-confirm
      @confirm="deleteChecked"
    >
      <v-card-text>
        {{ $t('shopping-list.are-you-sure-you-want-to-delete-checked-items') }}
      </v-card-text>
    </BaseDialog>

    <BasePageTitle divider>
      <template #header>
        <v-container>
          <v-row>
            <v-col
              class="text-left"
            >
              <ButtonLink
                :to="`/shopping-lists?disableRedirect=true`"
                :text="$t('shopping-list.all-lists')"
                :icon="$globals.icons.backArrow"
              />
            </v-col>
            <v-col
              v-if="mdAndUp"
              cols="6"
              class="d-none d-sm-flex justify-center"
            >
              <v-img
                max-height="100"
                max-width="100"
                :src="require('~/static/svgs/shopping-cart.svg')"
              />
            </v-col>
            <v-col class="d-flex justify-end">
              <BaseButtonGroup
                :buttons="[
                  {
                    icon: $globals.icons.contentCopy,
                    text: '',
                    event: 'edit',
                    children: [
                      {
                        icon: $globals.icons.contentCopy,
                        text: $t('shopping-list.copy-as-text'),
                        event: 'copy-plain',
                      },
                      {
                        icon: $globals.icons.contentCopy,
                        text: $t('shopping-list.copy-as-markdown'),
                        event: 'copy-markdown',
                      },
                    ],
                  },
                  {
                    icon: $globals.icons.checkboxOutline,
                    text: $t('shopping-list.check-all-items'),
                    event: 'check',
                  },
                  {
                    icon: $globals.icons.dotsVertical,
                    text: '',
                    event: 'three-dot',
                    children: [
                      {
                        icon: $globals.icons.tags,
                        text: $t('shopping-list.reorder-labels'),
                        event: 'reorder-labels',
                      },
                      {
                        icon: $globals.icons.tags,
                        text: $t('shopping-list.manage-labels'),
                        event: 'manage-labels',
                      },
                    ],
                  },
                ]"
                @edit="edit = true"
                @three-dot="threeDot = true"
                @check="openCheckAll"
                @copy-plain="copyListItems('plain')"
                @copy-markdown="copyListItems('markdown')"
                @reorder-labels="toggleReorderLabelsDialog()"
                @manage-labels="$router.push(`/group/data/labels`)"
              />
            </v-col>
          </v-row>
        </v-container>
      </template>
      <template #title>
        {{ shoppingList.name }}
      </template>
    </BasePageTitle>
    <BannerWarning
      v-if="isOffline"
      :title="$t('shopping-list.you-are-offline')"
      :description="$t('shopping-list.you-are-offline-description')"
    />

    <!-- Viewer -->
    <section
      v-if="!edit"
      class="py-2"
    >
      <!-- Create Item -->
      <div v-if="createEditorOpen">
        <ShoppingListItemEditor
          v-model="createListItemData"
          class="my-4"
          :labels="allLabels || []"
          :units="allUnits || []"
          :foods="allFoods || []"
          :allow-delete="false"
          @delete="createEditorOpen = false"
          @cancel="createEditorOpen = false"
          @save="createListItem"
        />
      </div>
      <div v-else class="d-flex justify-end">
        <BaseButton
          create
          @click="createEditorOpen = true"
        >
          {{ $t('general.add') }}
        </BaseButton>
      </div>

      <div
        v-for="(value, key) in itemsByLabel"
        :key="key"
        class="pb-4"
      >
        <v-btn
          :color="getLabelColor(value[0]) ? getLabelColor(value[0]) : '#959595'"
          :style="{
            'color': getTextColor(getLabelColor(value[0])),
            'letter-spacing': 'normal',
          }"
          @click="toggleShowLabel(key.toString())"
        >
          <v-icon>
            {{ labelOpenState[key] ? $globals.icons.chevronDown : $globals.icons.chevronRight }}
          </v-icon>
          {{ key }}
        </v-btn>
        <v-divider />
        <v-expand-transition>
          <div v-if="labelOpenState[key]">
            <VueDraggable
              :model-value="value"
              handle=".handle"
              :delay="250"
              :delay-on-touch-only="true"
              @start="loadingCounter += 1"
              @end="loadingCounter -= 1"
              @update:model-value="updateIndexUncheckedByLabel(key.toString(), $event)"
            >
              <v-lazy
                v-for="(item, index) in value"
                :key="item.id"
                class="ml-2 my-2"
              >
                <ShoppingListItem
                  v-model="value[index]"
                  :labels="allLabels || []"
                  :units="allUnits || []"
                  :foods="allFoods || []"
                  :recipes="recipeMap"
                  @checked="saveListItem"
                  @save="saveListItem"
                  @delete="deleteListItem(item)"
                />
              </v-lazy>
            </VueDraggable>
          </div>
        </v-expand-transition>
      </div>

      <!-- Reorder Labels -->
      <BaseDialog
        v-model="reorderLabelsDialog"
        :icon="$globals.icons.tagArrowUp"
        :title="$t('shopping-list.reorder-labels')"
        :submit-icon="$globals.icons.save"
        :submit-text="$t('general.save')"
        can-submit
        @submit="saveLabelOrder"
        @close="cancelLabelOrder"
      >
        <v-card
          height="fit-content"
          max-height="70vh"
          style="overflow-y: auto;"
        >
          <VueDraggable
            v-if="localLabels"
            v-model="localLabels"
            handle=".handle"
            :delay="250"
            :delay-on-touch-only="true"
            class="my-2"
            @update:model-value="updateLabelOrder"
          >
            <div
              v-for="(labelSetting, index) in localLabels"
              :key="labelSetting.id"
            >
              <MultiPurposeLabelSection
                v-model="localLabels[index]"
                use-color
              />
            </div>
          </VueDraggable>
        </v-card>
      </BaseDialog>

      <!-- Checked Items -->
      <div
        v-if="listItems.checked && listItems.checked.length > 0"
        class="mt-6"
      >
        <div class="d-flex">
          <div class="flex-grow-1">
            <button @click="toggleShowChecked()">
              <span>
                <v-icon>
                  {{ showChecked ? $globals.icons.chevronDown : $globals.icons.chevronRight }}
                </v-icon>
              </span>
              {{ $t('shopping-list.items-checked-count', listItems.checked ? listItems.checked.length : 0) }}
            </button>
          </div>
          <div class="justify-end mt-n2">
            <BaseButtonGroup
              :buttons="[
                {
                  icon: $globals.icons.checkboxBlankOutline,
                  text: $t('shopping-list.uncheck-all-items'),
                  event: 'uncheck',
                },
                {
                  icon: $globals.icons.delete,
                  text: $t('shopping-list.delete-checked'),
                  event: 'delete',
                },
              ]"
              @uncheck="openUncheckAll"
              @delete="openDeleteChecked"
            />
          </div>
        </div>
        <v-divider class="my-4" />
        <v-expand-transition>
          <div v-if="showChecked">
            <div
              v-for="(item, idx) in listItems.checked"
              :key="item.id"
            >
              <ShoppingListItem
                v-model="listItems.checked[idx]"
                class="strike-through-note"
                :labels="allLabels || []"
                :units="allUnits || []"
                :foods="allFoods || []"
                @checked="saveListItem"
                @save="saveListItem"
                @delete="deleteListItem(item)"
              />
            </div>
          </div>
        </v-expand-transition>
      </div>
    </section>

    <!-- Recipe References -->
    <v-lazy
      v-if="shoppingList.recipeReferences && shoppingList.recipeReferences.length > 0"
    >
      <section>
        <div>
          <span>
            <v-icon start class="mb-1">
              {{ $globals.icons.primary }}
            </v-icon>
          </span>
          {{ $t('shopping-list.linked-recipes-count', shoppingList.recipeReferences
            ? shoppingList.recipeReferences.length
            : 0) }}
        </div>
        <v-divider class="my-4" />
        <RecipeList
          :recipes="recipeList"
          show-description
          :disabled="isOffline"
        >
          <template
            v-for="(recipe, index) in recipeList"
            #[`actions-${recipe.id}`]
            :key="'item-actions-decrease' + recipe.id"
          >
            <v-list-item-action>
              <v-btn
                v-if="recipe"
                icon
                flat
                class="bg-transparent"
                :disabled="isOffline"
                @click.prevent="removeRecipeReferenceToList(recipe.id!)"
              >
                <v-icon color="grey-lighten-1">
                  {{ $globals.icons.minus }}
                </v-icon>
              </v-btn>
            </v-list-item-action>
            <div class="pl-3">
              {{ shoppingList.recipeReferences[index].recipeQuantity }}
            </div>
            <v-list-item-action>
              <v-btn
                icon
                :disabled="isOffline"
                flat
                class="bg-transparent"
                @click.prevent="addRecipeReferenceToList(recipe.id!)"
              >
                <v-icon color="grey-lighten-1">
                  {{ $globals.icons.createAlt }}
                </v-icon>
              </v-btn>
            </v-list-item-action>
          </template>
        </RecipeList>
      </section>
    </v-lazy>
    <WakelockSwitch />
  </v-container>
</template>

<script lang="ts">
import { VueDraggable } from "vue-draggable-plus";
import MultiPurposeLabelSection from "~/components/Domain/ShoppingList/MultiPurposeLabelSection.vue";
import ShoppingListItem from "~/components/Domain/ShoppingList/ShoppingListItem.vue";
import RecipeList from "~/components/Domain/Recipe/RecipeList.vue";
import ShoppingListItemEditor from "~/components/Domain/ShoppingList/ShoppingListItemEditor.vue";
import { useFoodStore, useLabelStore, useUnitStore } from "~/composables/store";
import { useShoppingListPreferences } from "~/composables/use-users/preferences";
import { getTextColor } from "~/composables/use-text-color";
import { useShoppingListPage } from "~/composables/shopping-list-page/use-shopping-list-page";

export default defineNuxtComponent({
  components: {
    VueDraggable,
    MultiPurposeLabelSection,
    ShoppingListItem,
    RecipeList,
    ShoppingListItemEditor,
  },
  setup() {
    const { mdAndUp } = useDisplay();
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const preferences = useShoppingListPreferences();

    useSeoMeta({
      title: i18n.t("shopping-list.shopping-list"),
    });

    const route = useRoute();
    const groupSlug = computed(() => route.params.groupSlug as string || $auth.user.value?.groupSlug || "");
    const id = route.params.id as string;

    const shoppingListPage = useShoppingListPage(id);
    const { store: allLabels } = useLabelStore();
    const { store: allUnits } = useUnitStore();
    const { store: allFoods } = useFoodStore();

    return {
      groupSlug,
      preferences,
      allLabels,
      allUnits,
      allFoods,
      getTextColor,
      mdAndUp,
      ...shoppingListPage,
    };
  },
});
</script>

<style scoped>
.number-input-container {
  max-width: 50px;
}
</style>
