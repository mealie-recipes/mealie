<template>
  <v-data-table
    v-model="selected"
    item-key="id"
    show-select
    :sort-by="sortBy"
    :headers="headers"
    :items="recipes"
    :items-per-page="15"
    class="elevation-0"
    :loading="loading"
    return-object
  >
    <template #[`item.name`]="{ item }">
      <a
        :href="`/g/${groupSlug}/r/${item.slug}`"
        style="color: inherit; text-decoration: inherit; "
        @click="$emit('click')"
      >{{ item.name }}</a>
    </template>
    <template #[`item.tags`]="{ item }">
      <RecipeChip
        small
        :items="item.tags!"
        :is-category="false"
        url-prefix="tags"
        @item-selected="filterItems"
      />
    </template>
    <template #[`item.recipeCategory`]="{ item }">
      <RecipeChip
        small
        :items="item.recipeCategory!"
        @item-selected="filterItems"
      />
    </template>
    <template #[`item.tools`]="{ item }">
      <RecipeChip
        small
        :items="item.tools"
        url-prefix="tools"
        @item-selected="filterItems"
      />
    </template>
    <template #[`item.userId`]="{ item }">
      <div class="d-flex align-center">
        <UserAvatar
          :user-id="item.userId!"
          :tooltip="false"
          size="40"
        />
        <div class="pl-2">
          <span class="text-left">
            {{ getMember(item.userId!) }}
          </span>
        </div>
      </div>
    </template>
    <template #[`item.dateAdded`]="{ item }">
      {{ formatDate(item.dateAdded!) }}
    </template>
  </v-data-table>
</template>

<script lang="ts">
import UserAvatar from "../User/UserAvatar.vue";
import RecipeChip from "./RecipeChips.vue";
import type { Recipe, RecipeCategory, RecipeTool } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import type { UserSummary } from "~/lib/api/types/user";
import type { RecipeTag } from "~/lib/api/types/household";

const INPUT_EVENT = "update:modelValue";

interface ShowHeaders {
  id: boolean;
  owner: boolean;
  tags: boolean;
  categories: boolean;
  tools: boolean;
  recipeServings: boolean;
  recipeYieldQuantity: boolean;
  recipeYield: boolean;
  dateAdded: boolean;
}

export default defineNuxtComponent({
  components: { RecipeChip, UserAvatar },
  props: {
    modelValue: {
      type: Array as PropType<Recipe[]>,
      required: false,
      default: () => [],
    },
    loading: {
      type: Boolean,
      required: false,
      default: false,
    },
    recipes: {
      type: Array as () => Recipe[],
      default: () => [],
    },
    showHeaders: {
      type: Object as () => ShowHeaders,
      required: false,
      default: () => {
        return {
          id: true,
          owner: false,
          tags: true,
          categories: true,
          recipeServings: true,
          recipeYieldQuantity: true,
          recipeYield: true,
          dateAdded: true,
        };
      },
    },
  },
  emits: ["click", "update:modelValue"],
  setup(props, context) {
    const i18n = useI18n();
    const $auth = useMealieAuth();
    const groupSlug = $auth.user.value?.groupSlug;
    const router = useRouter();
    const selected = computed({
      get: () => props.modelValue,
      set: value => context.emit(INPUT_EVENT, value),
    });

    // Initialize sort state with default sorting by dateAdded descending
    const sortBy = ref([{ key: "dateAdded", order: "desc" }]);

    const headers = computed(() => {
      const hdrs: Array<{ title: string; value: string; align?: string; sortable?: boolean }> = [];

      if (props.showHeaders.id) {
        hdrs.push({ title: i18n.t("general.id"), value: "id" });
      }
      if (props.showHeaders.owner) {
        hdrs.push({ title: i18n.t("general.owner"), value: "userId", align: "center", sortable: true });
      }
      hdrs.push({ title: i18n.t("general.name"), value: "name", sortable: true });
      if (props.showHeaders.categories) {
        hdrs.push({ title: i18n.t("recipe.categories"), value: "recipeCategory", sortable: true });
      }

      if (props.showHeaders.tags) {
        hdrs.push({ title: i18n.t("tag.tags"), value: "tags", sortable: true });
      }
      if (props.showHeaders.tools) {
        hdrs.push({ title: i18n.t("tool.tools"), value: "tools", sortable: true });
      }
      if (props.showHeaders.recipeServings) {
        hdrs.push({ title: i18n.t("recipe.servings"), value: "recipeServings", sortable: true });
      }
      if (props.showHeaders.recipeYieldQuantity) {
        hdrs.push({ title: i18n.t("recipe.yield"), value: "recipeYieldQuantity", sortable: true });
      }
      if (props.showHeaders.recipeYield) {
        hdrs.push({ title: i18n.t("recipe.yield-text"), value: "recipeYield", sortable: true });
      }
      if (props.showHeaders.dateAdded) {
        hdrs.push({ title: i18n.t("general.date-added"), value: "dateAdded", sortable: true });
      }

      return hdrs;
    });

    function formatDate(date: string) {
      try {
        return i18n.d(Date.parse(date), "medium");
      }
      catch {
        return "";
      }
    }

    // ============
    // Group Members
    const api = useUserApi();
    const members = ref<UserSummary[]>([]);

    async function refreshMembers() {
      const { data } = await api.groups.fetchMembers();
      if (data) {
        members.value = data.items;
      }
    }

    function filterItems(item: RecipeTag | RecipeCategory | RecipeTool, itemType: string) {
      if (!groupSlug || !item.id) {
        return;
      }
      router.push(`/g/${groupSlug}?${itemType}=${item.id}`);
    }

    onMounted(() => {
      refreshMembers();
    });

    function getMember(id: string) {
      if (members.value[0]) {
        return members.value.find(m => m.id === id)?.fullName;
      }

      return i18n.t("general.none");
    }

    return {
      selected,
      sortBy,
      groupSlug,
      headers,
      formatDate,
      members,
      getMember,
      filterItems,
    };
  },
});
</script>
