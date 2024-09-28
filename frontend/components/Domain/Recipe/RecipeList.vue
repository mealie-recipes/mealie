<template>
  <v-list :class="tile ? 'd-flex flex-wrap background' : 'background'">
    <v-sheet
      v-for="recipe, index in recipes"
      :key="recipe.id"
      :elevation="2"
      :class="attrs.class.sheet"
      :style="tile ? 'max-width: 100%; width: fit-content;' : 'width: 100%;'"
    >
      <v-list-item :to="disabled ? '' : '/g/' + groupSlug + '/r/' + recipe.slug" :class="attrs.class.listItem">
        <v-list-item-avatar :class="attrs.class.avatar">
          <v-icon :class="attrs.class.icon" dark :small="small"> {{ $globals.icons.primary }} </v-icon>
        </v-list-item-avatar>
        <v-list-item-content :class="attrs.class.text">
          <v-list-item-title :class="listItem && listItemDescriptions[index] ? '' : 'pr-4'" :style="attrs.style.text.title">
            {{ recipe.name }}
          </v-list-item-title>
          <v-list-item-subtitle v-if="showDescription">{{ recipe.description }}</v-list-item-subtitle>
          <v-list-item-subtitle v-if="listItem && listItemDescriptions[index]" :style="attrs.style.text.subTitle">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div v-html="listItemDescriptions[index]"></div>
          </v-list-item-subtitle>
        </v-list-item-content>
        <slot :name="'actions-' + recipe.id" :v-bind="{ item: recipe }"> </slot>
      </v-list-item>
    </v-sheet>
  </v-list>
</template>

<script lang="ts">
import { computed, defineComponent, useContext, useRoute } from "@nuxtjs/composition-api";
import DOMPurify from "dompurify";
import { useFraction } from "~/composables/recipes/use-fraction";
import { ShoppingListItemOut } from "~/lib/api/types/household";
import { RecipeSummary } from "~/lib/api/types/recipe";

export default defineComponent({
  props: {
    recipes: {
      type: Array as () => RecipeSummary[],
      required: true,
    },
    listItem: {
      type: Object as () => ShoppingListItemOut | undefined,
      default: undefined,
    },
    small: {
      type: Boolean,
      default: false,
    },
    tile: {
      type: Boolean,
      default: false,
    },
    showDescription: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    }
  },
  setup(props) {
    const { $auth } = useContext();
    const { frac } = useFraction();
    const route = useRoute();
    const groupSlug = computed(() => route.value.params.groupSlug || $auth.user?.groupSlug || "");

    const attrs = computed(() => {
      return props.small ? {
        class: {
          sheet: props.tile ? "mb-1 me-1 justify-center align-center" : "mb-1 justify-center align-center",
          listItem: "px-0",
          avatar: "ma-0",
          icon: "ma-0 pa-0 primary",
          text: "pa-0",
        },
        style: {
          text: {
            title: "font-size: small;",
            subTitle: "font-size: x-small;",
          },
        },
      } : {
        class: {
          sheet: props.tile ? "mx-1 justify-center align-center" : "mb-1 justify-center align-center",
          listItem: "px-4",
          avatar: "",
          icon: "pa-1 primary",
          text: "",
        },
        style: {
          text: {
            title: "",
            subTitle: "",
          },
        },
      }
    });

    function sanitizeHTML(rawHtml: string) {
      return DOMPurify.sanitize(rawHtml, {
        USE_PROFILES: { html: true },
        ALLOWED_TAGS: ["strong", "sup"],
      });
    }

    const listItemDescriptions = computed<string[]>(() => {
      if (
          props.recipes.length === 1  // we don't need to specify details if there's only one recipe ref
          || !props.listItem?.recipeReferences
          || props.listItem.recipeReferences.length !== props.recipes.length
        ) {
        return props.recipes.map((_) => "")
      }

      const listItemDescriptions: string[] = [];
      for (let i = 0; i < props.recipes.length; i++) {
        const itemRef = props.listItem?.recipeReferences[i];
        const quantity = (itemRef.recipeQuantity || 1) * (itemRef.recipeScale || 1);

        let listItemDescription = ""
        if (props.listItem.unit?.fraction) {
            const fraction = frac(quantity, 10, true);
            if (fraction[0] !== undefined && fraction[0] > 0) {
              listItemDescription += fraction[0];
            }

            if (fraction[1] > 0) {
              listItemDescription += ` <sup>${fraction[1]}</sup>&frasl;<sub>${fraction[2]}</sub>`;
            }
            else {
              listItemDescription = (quantity).toString();
            }
          }
          else {
            listItemDescription = (Math.round(quantity*100)/100).toString();
          }

          if (props.listItem.unit) {
            const unitDisplay = props.listItem.unit.useAbbreviation && props.listItem.unit.abbreviation
              ? props.listItem.unit.abbreviation : props.listItem.unit.name;

            listItemDescription += ` ${unitDisplay}`
          }

          if (itemRef.recipeNote) {
            listItemDescription += `, ${itemRef.recipeNote}`
          }

          listItemDescriptions.push(sanitizeHTML(listItemDescription));
      }

      return listItemDescriptions;
    });

    return {
      attrs,
      groupSlug,
      listItemDescriptions,
    };
  },
});
</script>
