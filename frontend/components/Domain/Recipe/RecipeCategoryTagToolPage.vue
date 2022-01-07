<template>
  <div v-if="items">
    <v-app-bar color="transparent" flat class="mt-n1 rounded">
      <v-icon large left>
        {{ icon }}
      </v-icon>
      <v-toolbar-title class="headline"> {{ headline }} </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <section v-for="(itms, key, idx) in itemsSorted" :key="'header' + idx" :class="idx === 1 ? null : 'my-4'">
      <BaseCardSectionTitle :title="key"> </BaseCardSectionTitle>
      <v-row>
        <v-col v-for="(item, index) in itms" :key="'cat' + index" cols="12" :sm="12" :md="6" :lg="4" :xl="3">
          <v-card class="left-border" hover :to="`/recipes/${itemType}/${item.slug}`">
            <v-card-actions>
              <v-icon>
                {{ icon }}
              </v-icon>
              <v-card-title class="py-1">{{ item.name }}</v-card-title>
              <v-spacer></v-spacer>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </section>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs, useContext, computed } from "@nuxtjs/composition-api";

type ItemType = "tags" | "categories" | "tools";

const ItemTypes = {
  tag: "tags",
  category: "categories",
  tool: "tools",
};

interface GenericItem {
  name: string;
  slug: string;
}

export default defineComponent({
  props: {
    itemType: {
      type: String as () => ItemType,
      required: true,
    },
    items: {
      type: Array as () => GenericItem[],
      required: true,
    },
  },
  setup(props) {
    // @ts-ignore
    const { i18n, $globals } = useContext();

    const state = reactive({
      headline: "tags",
      icon: $globals.icons.tags,
    });

    switch (props.itemType) {
      case ItemTypes.tag:
        state.headline = i18n.t("tag.tags") as string;
        break;
      case ItemTypes.category:
        state.headline = i18n.t("category.categories") as string;
        break;
      case ItemTypes.tool:
        state.headline = i18n.t("tool.tools") as string;
        state.icon = $globals.icons.potSteam;
        break;
      default:
        break;
    }

    const itemsSorted = computed(() => {
      const byLetter: { [key: string]: Array<any> } = {};

      if (!props.items) return byLetter;

      props.items.forEach((item) => {
        const letter = item.name[0].toUpperCase();
        if (!byLetter[letter]) {
          byLetter[letter] = [];
        }

        byLetter[letter].push(item);
      });

      return byLetter;
    });

    return {
      ...toRefs(state),
      itemsSorted,
    };
  },
  head() {
    return {
      title: this.headline as string,
    }
  },
});
</script>
