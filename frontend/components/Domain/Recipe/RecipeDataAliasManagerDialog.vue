<template>
  <div>
    <BaseDialog
      v-model="dialog"
      :title="$t('data-pages.manage-aliases')"
      :icon="$globals.icons.edit"
      :submit-icon="$globals.icons.check"
      :submit-text="$t('general.confirm')"
      can-submit
      @submit="saveAliases"
      @cancel="$emit('cancel')"
    >
      <v-card-text>
        <v-container>
          <v-row v-for="alias, i in aliases" :key="i">
            <v-col cols="10">
              <v-text-field v-model="alias.name" :label="$t('general.name')" :rules="[validators.required]" />
            </v-col>
            <v-col cols="2">
              <BaseButtonGroup
                :buttons="[
                  {
                    icon: $globals.icons.delete,
                    text: $t('general.delete'),
                    event: 'delete',
                  },
                ]"
                @delete="deleteAlias(i)"
              />
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton edit @click="createAlias">
          {{ $t('data-pages.create-alias') }}
          <template #icon>
            {{ $globals.icons.create }}
          </template>
        </BaseButton>
      </template>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { whenever } from "@vueuse/core";
import { validators } from "~/composables/use-validators";
import type { IngredientFood, IngredientUnit } from "~/lib/api/types/recipe";

export interface GenericAlias {
  name: string;
}

interface Props {
  data: IngredientFood | IngredientUnit;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  submit: [aliases: GenericAlias[]];
  cancel: [];
}>();

// V-Model Support
const dialog = defineModel<boolean>({ default: false });

function createAlias() {
  aliases.value.push({
    name: "",
  });
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
  () => dialog.value,
  () => {
    initAliases();
  },
);

function saveAliases() {
  const seenAliasNames: string[] = [];
  const keepAliases: GenericAlias[] = [];
  aliases.value.forEach((alias) => {
    if (
      !alias.name
      || alias.name === props.data.name
      || alias.name === props.data.pluralName
      || alias.name === props.data.abbreviation
      || alias.name === props.data.pluralAbbreviation
      || seenAliasNames.includes(alias.name)
    ) {
      return;
    }

    keepAliases.push(alias);
    seenAliasNames.push(alias.name);
  });

  aliases.value = keepAliases;
  emit("submit", keepAliases);
}
</script>
