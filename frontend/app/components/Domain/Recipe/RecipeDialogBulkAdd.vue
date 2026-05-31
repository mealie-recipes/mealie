<template>
  <div class="text-center">
    <BaseButton @click="dialog = true">
      {{ $t("new-recipe.bulk-add") }}
    </BaseButton>
    <BaseDialog
      v-model="dialog"
      width="800"
      :title="$t('new-recipe.bulk-add')"
      :icon="$globals.icons.createAlt"
      :submit-text="$t('general.add')"
      :disable-submit-on-enter="true"
      can-submit
      @submit="save"
    >
      <v-card-text>
        <v-textarea
          v-model="inputText"
          variant="outlined"
          rows="12"
          hide-details
          autofocus
          :placeholder="$t('new-recipe.paste-in-your-recipe-data-each-line-will-be-treated-as-an-item-in-a-list')"
        />

        <v-divider />
        <v-list lines="two">
          <template
            v-for="(util) in utilities"
            :key="util.id"
          >
            <v-list-item
              class="px-0"
            >
              <template #prepend>
                <v-avatar>
                  <v-btn
                    icon
                    variant="tonal"
                    base-color="info"
                    :title="$t('general.run')"
                    @click="util.action"
                  >
                    <v-icon>
                      {{ $globals.icons.play }}
                    </v-icon>
                  </v-btn>
                </v-avatar>
              </template>
              <v-list-item-title class="text-pre-wrap">
                {{ util.description }}
              </v-list-item-title>
            </v-list-item>
          </template>
        </v-list>
      </v-card-text>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
interface Props {
  inputTextProp?: string;
}
const props = withDefaults(defineProps<Props>(), {
  inputTextProp: "",
});

const emit = defineEmits<{
  "bulk-data": [data: string[]];
}>();

const dialog = ref(false);
const inputText = ref(props.inputTextProp);

function splitText() {
  return inputText.value.split("\n").filter(line => !(line === "\n" || !line));
}

function removeFirstCharacter() {
  inputText.value = splitText()
    .map(line => line.substring(1))
    .join("\n");
}

const numberedLineRegex = /\d+[.):] /gm;

function splitByNumberedLine() {
  // Split inputText by numberedLineRegex
  const matches = inputText.value.match(numberedLineRegex);

  matches?.forEach((match, idx) => {
    const replaceText = idx === 0 ? "" : "\n";
    inputText.value = inputText.value.replace(match, replaceText);
  });
}

function trimAllLines() {
  const splitLines = splitText();

  splitLines.forEach((element: string, index: number) => {
    splitLines[index] = element.trim();
  });

  inputText.value = splitLines.join("\n");
}

function save() {
  emit("bulk-data", splitText());
  dialog.value = false;
}

function open() {
  dialog.value = true;
}
function close() {
  dialog.value = false;
}

const i18n = useI18n();

const utilities = [
  {
    id: "trim-whitespace",
    description: i18n.t("new-recipe.trim-whitespace-description"),
    action: trimAllLines,
  },
  {
    id: "trim-prefix",
    description: i18n.t("new-recipe.trim-prefix-description"),
    action: removeFirstCharacter,
  },
  {
    id: "split-by-numbered-line",
    description: i18n.t("new-recipe.split-by-numbered-line-description"),
    action: splitByNumberedLine,
  },
];

// Expose functions to parent components
defineExpose({
  open,
  close,
});
</script>
