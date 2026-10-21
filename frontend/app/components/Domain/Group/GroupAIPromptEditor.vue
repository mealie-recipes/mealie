<template>
  <div>
    <BaseCardSectionTitle :title="$t('group.ai-prompts.ai-prompts')" />
    <v-card-text class="pt-0 pb-6 px-0">
      {{ $t("group.ai-prompts.ai-prompts-description") }}
    </v-card-text>

    <AppLoader v-if="!prompts" />
    <template v-else>
      <BaseCardSectionTitle :title="$t('group.ai-prompts.global-instructions')" size="medium" />
      <v-card-subtitle class="px-0 mb-2" style="white-space: normal;">
        {{ $t("group.ai-prompts.global-instructions-description") }}
      </v-card-subtitle>
      <v-textarea
        v-model="globalDraft"
        :placeholder="$t('group.ai-prompts.global-instructions-placeholder')"
        variant="outlined"
        auto-grow
        rows="2"
        hide-details
      />
      <div class="d-flex pt-2 pb-6">
        <BaseButton
          save
          class="ml-auto"
          :disabled="globalDraft.trim() === (prompts.globalInstructions ?? '')"
          :loading="loading"
          @click="saveGlobal"
        />
      </div>

      <BaseCardSectionTitle :title="$t('group.ai-prompts.prompts')" size="medium" class="pb-2" />
      <v-expansion-panels variant="accordion">
        <v-expansion-panel v-for="prompt in prompts.prompts" :key="prompt.name" :value="prompt.name">
          <v-expansion-panel-title>
            <div class="d-flex align-center flex-wrap ga-2">
              <span>{{ promptTitle(prompt.name) }}</span>
              <v-chip v-if="prompt.isSystem" size="x-small" label>
                {{ $t("group.ai-prompts.system") }}
              </v-chip>
              <v-chip v-if="prompt.mode" size="x-small" label color="primary">
                {{ prompt.mode === "override" ? $t("group.ai-prompts.overridden") : $t("group.ai-prompts.appended") }}
              </v-chip>
              <v-icon v-if="prompt.defaultChanged" size="small" color="warning">
                {{ $globals.icons.alert }}
              </v-icon>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text v-if="drafts[prompt.name]">
            <p class="mb-4">
              {{ promptDescription(prompt.name) }}
            </p>
            <v-alert v-if="prompt.isSystem" type="warning" variant="tonal" density="compact" class="mb-4">
              {{ $t("group.ai-prompts.system-description") }}
            </v-alert>

            <v-alert v-if="prompt.defaultChanged" type="warning" variant="tonal" density="compact" class="mb-4">
              {{ $t("group.ai-prompts.default-changed") }}
            </v-alert>

            <v-btn-toggle
              :model-value="drafts[prompt.name]!.mode"
              mandatory
              divided
              variant="outlined"
              density="compact"
              color="primary"
              class="mt-2 mb-4"
              @update:model-value="(mode: DraftMode) => setMode(prompt, mode)"
            >
              <v-btn value="default">
                {{ $t("group.ai-prompts.mode-default") }}
              </v-btn>
              <v-btn value="append">
                {{ $t("group.ai-prompts.mode-append") }}
              </v-btn>
              <v-btn value="override">
                {{ $t("group.ai-prompts.mode-override") }}
              </v-btn>
            </v-btn-toggle>

            <template v-if="drafts[prompt.name]!.mode === 'append'">
              <p class="mb-2">
                {{ $t("group.ai-prompts.append-description") }}
              </p>
              <v-textarea
                v-model="drafts[prompt.name]!.append"
                variant="outlined"
                auto-grow
                rows="3"
                hide-details
              />
            </template>

            <template v-else-if="drafts[prompt.name]!.mode === 'override'">
              <v-alert type="info" variant="tonal" density="compact" class="mb-4">
                {{ $t("group.ai-prompts.override-description") }}
              </v-alert>
              <v-textarea
                v-model="drafts[prompt.name]!.override"
                variant="outlined"
                auto-grow
                rows="6"
                hide-details
              />
            </template>

            <div class="d-flex align-center flex-wrap ga-2 pt-2">
              <BaseButton
                color="info"
                :icon="drafts[prompt.name]!.showDefault ? $globals.icons.eyeOff : $globals.icons.eye"
                :text="drafts[prompt.name]!.showDefault
                  ? $t('group.ai-prompts.hide-default-prompt')
                  : $t('group.ai-prompts.view-default-prompt')"
                @click="drafts[prompt.name]!.showDefault = !drafts[prompt.name]!.showDefault"
              />
              <BaseButton
                save
                class="ml-auto"
                :disabled="!isDirty(prompt)"
                :loading="loading"
                @click="savePrompt(prompt)"
              />
            </div>

            <v-textarea
              v-if="drafts[prompt.name]!.showDefault"
              :model-value="prompt.defaultContent"
              :label="$t('group.ai-prompts.default-prompt')"
              variant="outlined"
              auto-grow
              readonly
              hide-details
              class="mt-4"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useAIPrompts } from "~/composables/use-ai-providers";
import { alert } from "~/composables/use-toast";
import type { AIPromptOut } from "~/lib/api/types/group";

const GLOBAL_PROMPT_NAME = "global";

type DraftMode = "default" | "append" | "override";

interface Draft {
  mode: DraftMode;
  append: string;
  override: string;
  showDefault: boolean;
}

const props = defineProps<{
  /** Set when an admin is managing another group's prompts */
  groupId?: string;
}>();

const i18n = useI18n();
const { prompts, loading, refresh, save, reset } = useAIPrompts(
  props.groupId === undefined ? undefined : () => props.groupId,
);

const globalDraft = ref("");
const drafts = reactive<Record<string, Draft>>({});

function syncDraft(prompt: AIPromptOut) {
  drafts[prompt.name] = {
    mode: prompt.mode ?? "default",
    append: prompt.mode === "append" ? prompt.content ?? "" : "",
    override: prompt.mode === "override" ? prompt.content ?? "" : "",
    showDefault: drafts[prompt.name]?.showDefault ?? false,
  };
}

// Only the prompt that was saved is synced, so unsaved edits to the others aren't lost
function syncFromServer(name?: string) {
  if (!prompts.value) {
    return;
  }

  if (!name || name === GLOBAL_PROMPT_NAME) {
    globalDraft.value = prompts.value.globalInstructions ?? "";
  }

  for (const prompt of prompts.value.prompts) {
    if (!name || prompt.name === name) {
      syncDraft(prompt);
    }
  }
}

watch(() => props.groupId, async () => {
  await refresh();
  syncFromServer();
}, { immediate: true });

function promptKey(name: string) {
  return name.replaceAll(".", "-");
}

function promptTitle(name: string) {
  const key = `group.ai-prompts.prompt-titles.${promptKey(name)}`;
  return i18n.te(key) ? i18n.t(key) : name;
}

function promptDescription(name: string) {
  const key = `group.ai-prompts.prompt-descriptions.${promptKey(name)}`;
  return i18n.te(key) ? i18n.t(key) : "";
}

function setMode(prompt: AIPromptOut, mode: DraftMode) {
  const draft = drafts[prompt.name]!;
  draft.mode = mode;

  // An override starts from the built-in prompt, so it can be edited rather than rewritten
  if (mode === "override" && !draft.override.trim()) {
    draft.override = prompt.defaultContent;
  }
}

function draftContent(draft: Draft) {
  return draft.mode === "override" ? draft.override : draft.append;
}

function isDirty(prompt: AIPromptOut) {
  const draft = drafts[prompt.name]!;
  if (draft.mode === "default") {
    return !!prompt.mode;
  }

  const content = draftContent(draft);
  return !!content.trim() && (draft.mode !== prompt.mode || content !== prompt.content);
}

function notify(data: unknown) {
  if (data) {
    alert.success(i18n.t("group.ai-prompts.prompt-saved"));
  }
  else {
    alert.error(i18n.t("group.ai-prompts.prompt-save-failed"));
  }
}

async function savePrompt(prompt: AIPromptOut) {
  const draft = drafts[prompt.name]!;
  const data = draft.mode === "default"
    ? await reset(prompt.name)
    : await save(prompt.name, { mode: draft.mode, content: draftContent(draft) });

  notify(data);
  if (data) {
    syncFromServer(prompt.name);
  }
}

async function saveGlobal() {
  const content = globalDraft.value.trim();
  const data = content
    ? await save(GLOBAL_PROMPT_NAME, { mode: "append", content })
    : await reset(GLOBAL_PROMPT_NAME);

  notify(data);
  if (data) {
    syncFromServer(GLOBAL_PROMPT_NAME);
  }
}
</script>
