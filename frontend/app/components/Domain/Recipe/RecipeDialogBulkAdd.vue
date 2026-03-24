<template>
  <div class="text-center">
    <v-dialog
      v-model="dialog"
      width="800"
    >
      <template #activator="{ props: activatorProps }">
        <BaseButton
          v-bind="activatorProps"
          @click="inputText = inputTextProp"
        >
          {{ $t("new-recipe.bulk-add") }}
        </BaseButton>
      </template>

      <v-card>
        <v-app-bar
          density="compact"
          dark
          color="primary"
          class="mb-2 position-relative left-0 top-0 w-100"
        >
          <v-icon
            size="large"
            start
          >
            {{ $globals.icons.createAlt }}
          </v-icon>
          <v-toolbar-title class="headline">
            {{ $t("new-recipe.bulk-add") }}
          </v-toolbar-title>
          <v-spacer />
        </v-app-bar>

        <v-card-text>
          <v-textarea
            v-model="inputText"
            variant="outlined"
            rows="12"
            hide-details
            :placeholder="$t('new-recipe.paste-in-your-recipe-data-each-line-will-be-treated-as-an-item-in-a-list')"
          />

          <v-divider />
          <template
            v-for="(util) in utilities"
            :key="util.id"
          >
            <v-list-item
              density="compact"
              class="py-1"
            >
              <v-list-item-title>
                <v-list-item-subtitle class="wrap-word">
                  {{ util.description }}
                </v-list-item-subtitle>
              </v-list-item-title>
              <BaseButton
                size="small"
                color="info"
                @click="util.action"
              >
                <template #icon>
                  {{ $globals.icons.robot }}
                </template>
                {{ $t("general.run") }}
              </BaseButton>
            </v-list-item>
            <v-divider class="mx-2" />
          </template>
        </v-card-text>

        <v-divider />

        <v-card-actions>
          <BaseButton
            cancel
            @click="dialog = false"
          />
          <v-spacer />
          <BaseButton
            save
            color="success"
            @click="save"
          />
        </v-card-actions>
      </v-card>
    </v-dialog>
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
