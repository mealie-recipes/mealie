<template>
  <v-container class="md-container">
    <BasePageTitle divider>
      <template #header>
        <v-img max-height="100" max-width="100" :src="require('~/static/svgs/manage-cookbooks.svg')"></v-img>
      </template>
      <template #title> Meal Plan Rules </template>
      You can create rules for auto selecting recipes for you meal plans. These rules are used by the server to
      determine the random pool of recipes to select from when creating meal plans. Note that if rules have the same
      day/type constraints then the categories of the rules will be merged. In practice, it's unnecessary to create
      duplicate rules, but it's possible to do so.
    </BasePageTitle>

    <v-card>
      <v-card-title class="headline"> New Rule </v-card-title>
      <v-divider class="mx-2"></v-divider>
      <v-card-text>
        When creating a new rule for a meal plan you can restrict the rule to be applicable for a specific day of the
        week and/or a specific type of meal. To apply a rule to all days or all meal types you can set the rule to "Any"
        which will apply it to all the possible values for the day and/or meal type.

        <GroupMealPlanRuleForm
          class="mt-2"
          :day.sync="createData.day"
          :entry-type.sync="createData.entryType"
          :categories.sync="createData.categories"
          :tags.sync="createData.tags"
        />
      </v-card-text>
      <v-card-actions class="justify-end">
        <BaseButton create @click="createRule" />
      </v-card-actions>
    </v-card>

    <section>
      <BaseCardSectionTitle class="mt-10" title="Recipe Rules" />
      <div>
        <div v-for="(rule, idx) in allRules" :key="rule.id">
          <v-card class="my-2 left-border">
            <v-card-title class="headline pb-1">
              {{ rule.day === "unset" ? "Applies to all days" : `Applies on ${rule.day}s` }}
              {{ rule.entryType === "unset" ? "for all meal types" : ` for ${rule.entryType} meal types` }}
              <span class="ml-auto">
                <BaseButtonGroup
                  :buttons="[
                    {
                      icon: $globals.icons.edit,
                      text: $tc('general.edit'),
                      event: 'edit',
                    },
                    {
                      icon: $globals.icons.delete,
                      text: $tc('general.delete'),
                      event: 'delete',
                    },
                  ]"
                  @delete="deleteRule(rule.id)"
                  @edit="toggleEditState(rule.id)"
                />
              </span>
            </v-card-title>
            <v-card-text>
              <template v-if="!editState[rule.id]">
                <div v-if="rule.categories">
                  <h4 class="py-1">{{ $t("category.categories") }}:</h4>
                  <RecipeChips :items="rule.categories" small />
                </div>

                <div v-if="rule.tags">
                  <h4 class="py-1">{{ $t("tag.tags") }}:</h4>
                  <RecipeChips :items="rule.tags" url-prefix="tags" small />
                </div>
              </template>
              <template v-else>
                <GroupMealPlanRuleForm
                  :day.sync="allRules[idx].day"
                  :entry-type.sync="allRules[idx].entryType"
                  :categories.sync="allRules[idx].categories"
                  :tags.sync="allRules[idx].tags"
                />
                <div class="d-flex justify-end">
                  <BaseButton update @click="updateRule(rule)" />
                </div>
              </template>
            </v-card-text>
          </v-card>
        </div>
      </div>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, useAsync } from "@nuxtjs/composition-api";
import { useUserApi } from "~/composables/api";
import { PlanRulesCreate, PlanRulesOut } from "~/types/api-types/meal-plan";
import GroupMealPlanRuleForm from "~/components/Domain/Group/GroupMealPlanRuleForm.vue";
import { useAsyncKey } from "~/composables/use-utils";
import RecipeChips from "~/components/Domain/Recipe/RecipeChips.vue";

export default defineComponent({
  components: {
    GroupMealPlanRuleForm,
    RecipeChips,
  },
  props: {
    value: {
      type: Boolean,
      default: false,
    },
  },
  setup() {
    const api = useUserApi();

    // ======================================================
    // Manage All
    const editState = ref<{ [key: string]: boolean }>({});
    const allRules = ref<PlanRulesOut[]>([]);

    function toggleEditState(id: string) {
      editState.value[id] = !editState.value[id];
      editState.value = { ...editState.value };
    }

    async function refreshAll() {
      const { data } = await api.mealplanRules.getAll();

      if (data) {
        allRules.value = data;
      }
    }

    useAsync(async () => {
      await refreshAll();
    }, useAsyncKey());

    // ======================================================
    // Creating Rules

    const createData = ref<PlanRulesCreate>({
      entryType: "unset",
      day: "unset",
      categories: [],
      tags: [],
    });

    async function createRule() {
      const { data } = await api.mealplanRules.createOne(createData.value);
      if (data) {
        refreshAll();
        createData.value = {
          entryType: "unset",
          day: "unset",
          categories: [],
          tags: [],
        };
      }
    }

    async function deleteRule(ruleId: string) {
      const { data } = await api.mealplanRules.deleteOne(ruleId);
      if (data) {
        refreshAll();
      }
    }

    async function updateRule(rule: PlanRulesOut) {
      const { data } = await api.mealplanRules.updateOne(rule.id, rule);
      if (data) {
        refreshAll();
        toggleEditState(rule.id);
      }
    }

    return {
      allRules,
      createData,
      createRule,
      deleteRule,
      editState,
      updateRule,
      toggleEditState,
    };
  },
  head: {
    title: "Meal Plan Settings",
  },
});
</script>
