<template>
  <div>
    <BaseDialog
      v-model="dialog"
      :title="$t('data-pages.manage-aliases')"
      :icon="$globals.icons.edit"
      :submit-icon="$globals.icons.check"
      :submit-text="$tc('general.confirm')"
      @submit="saveAliases"
      @cancel="$emit('cancel')"
    >
      <v-card-text>
        <v-container>
          <v-row v-for="alias, i in aliases" :key="i">
            <v-col cols="10">
              <v-text-field
                v-model="alias.name"
                :label="$t('general.name')"
                :rules="[validators.required]"
              />
            </v-col>
            <v-col cols="2">
              <BaseButtonGroup
                :buttons="[
                  {
                    icon: $globals.icons.delete,
                    text: $tc('general.delete'),
                    event: 'delete'
                  }
                ]"
                @delete="deleteAlias(i)"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton edit @click="createAlias">{{ $t('data-pages.create-alias') }}
          <template #icon>
            {{ $globals.icons.create }}
          </template>
        </BaseButton>
      </template>
    </BaseDialog>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from "@nuxtjs/composition-api";
import { whenever } from "@vueuse/core";
import { validators } from "~/composables/use-validators";
import { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";

export interface GenericAlias {
  name: string;
}

export default defineComponent({
  props: {
    value: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Object as () => IngredientFood | IngredientUnit,
      required: true,
    },
  },
  setup(props, context) {
    // V-Model Support
    const dialog = computed({
      get: () => {
        return props.value;
      },
      set: (val) => {
        context.emit("input", val);
      },
    });

    function createAlias() {
      aliases.value.push({
        "name": "",
      })
    }

    function deleteAlias(index: number) {
      aliases.value.splice(index, 1);
    }

    const aliases = ref<GenericAlias[]>(props.data.aliases || []);
    function initAliases() {
      aliases.value = [...props.data.aliases || []];
      if (!aliases.value.length) {
        createAlias();
      }
    }

    initAliases();
    whenever(
      () => props.value,
      () => {
        initAliases();
      },
    )

    function saveAliases() {
      const seenAliasNames: string[] = [];
      const keepAliases: GenericAlias[] = [];
      aliases.value.forEach((alias) => {
        if (
          !alias.name
          || alias.name === props.data.name
          || alias.name === props.data.pluralName
          // @ts-ignore only applies to units
          || alias.name === props.data.abbreviation
          // @ts-ignore only applies to units
          || alias.name === props.data.pluralAbbreviation
          || seenAliasNames.includes(alias.name)
        ) {
          return;
        }

        keepAliases.push(alias);
        seenAliasNames.push(alias.name);
      })

      aliases.value = keepAliases;
      context.emit("submit", keepAliases);
    }

    return {
      aliases,
      createAlias,
      dialog,
      deleteAlias,
      saveAliases,
      validators,
    }
  },
});
</script>
