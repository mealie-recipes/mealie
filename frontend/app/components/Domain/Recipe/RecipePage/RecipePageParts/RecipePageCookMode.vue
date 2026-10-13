<template>
  <v-theme-provider theme="dark">
    <!-- the class gives plain children the dark design tokens; the provider covers Vuetify ones -->
    <div
      class="cook-mode v-theme--dark"
      role="dialog"
      aria-modal="true"
      :aria-label="`${$t('recipe.cook-mode')}: ${recipe.name}`"
    >
      <!-- Top bar -->
      <header class="cook-bar">
        <button type="button" class="cook-pill" @click="exit">
          <svg width="11" height="11" viewBox="0 0 14 14" aria-hidden="true"><line
            x1="2"
            y1="2"
            x2="12"
            y2="12"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
          /><line
            x1="12"
            y1="2"
            x2="2"
            y2="12"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
          /></svg>
          {{ $t("cook-mode.exit") }}
        </button>
        <div class="cook-bar__title">
          <span class="cook-bar__name">{{ recipe.name }}</span>
          <span class="cook-bar__meta">{{ barMeta }}</span>
        </div>
        <button
          type="button"
          class="cook-pill"
          :class="{ 'cook-pill--active': panel === 'ingredients' }"
          :aria-pressed="panel === 'ingredients'"
          @click="togglePanel('ingredients')"
        >
          {{ $t("recipe.ingredients") }}
        </button>
      </header>

      <div v-if="steps.length" class="cook-progress" aria-hidden="true">
        <div
          v-for="(_, index) in steps"
          :key="index"
          class="cook-progress__segment"
          :class="{ 'cook-progress__segment--on': index <= current }"
        />
      </div>

      <div class="cook-body">
        <!-- Current step -->
        <main ref="stage" class="cook-stage">
          <div class="cook-stage__scroll">
            <div v-if="otherRunningTimers.length" class="cook-running">
              <button
                v-for="timer in otherRunningTimers"
                :key="timer.key"
                type="button"
                class="cook-running__timer"
                :class="{ 'cook-running__timer--done': timer.done }"
                @click="goTo(timer.step)"
              >
                <v-icon size="14">
                  {{ $globals.icons.timerOutline }}
                </v-icon>
                {{ $t("cook-mode.step-number", { step: timer.step + 1 }) }} · {{ formatTimer(timer.remaining) }}
              </button>
            </div>

            <template v-if="step">
              <div class="cook-stage__eyebrow">
                <template v-if="sectionTitle">
                  {{ sectionTitle }} ·
                </template>
                {{ $t("cook-mode.step-number", { step: current + 1 }) }}
              </div>
              <SafeMarkdown
                :key="current"
                class="cook-stage__text"
                :class="`cook-stage__text--${textSize}`"
                :source="highlightedText"
                aria-live="polite"
              />

              <div v-if="uses.length" class="cook-uses">
                <div v-for="(use, index) in uses" :key="index" class="cook-uses__chip">
                  <!-- eslint-disable-next-line vue/no-v-html -- sanitized by the ingredient parser -->
                  <span v-if="use.amount" class="cook-uses__amount" v-html="use.amount" />
                  <!-- eslint-disable-next-line vue/no-v-html -- sanitized by the ingredient parser -->
                  <span class="cook-uses__name" v-html="use.name" />
                </div>
              </div>

              <div v-if="notes.length" class="cook-notes">
                <div v-for="note in notes" :key="note.referenceId ?? note.title" class="cook-notes__note">
                  <div class="cook-notes__title">
                    {{ note.title || $t("recipe.note") }}
                  </div>
                  <SafeMarkdown :source="note.text" />
                </div>
              </div>

              <div
                v-for="(timer, index) in stepTimers"
                :key="`${current}-${index}`"
                class="cook-timer"
                :class="{ 'cook-timer--done': timerState(current, index).done }"
              >
                <div class="cook-timer__readout">
                  <span class="cook-timer__label">
                    {{ timerState(current, index).done ? $t("cook-mode.timer-done") : $t("cook-mode.timer") }}
                  </span>
                  <span class="cook-timer__time" role="timer">
                    {{ formatTimer(timerState(current, index).remaining) }}
                  </span>
                </div>
                <div class="cook-timer__controls">
                  <button
                    v-if="timerState(current, index).started"
                    type="button"
                    class="cook-timer__reset"
                    :aria-label="$t('general.reset')"
                    :title="$t('general.reset')"
                    @click="resetTimer(current, index)"
                  >
                    <v-icon size="20">
                      {{ $globals.icons.restart }}
                    </v-icon>
                  </button>
                  <button
                    v-if="!timerState(current, index).done"
                    type="button"
                    class="cook-timer__toggle"
                    @click="toggleTimer(current, index, timer.seconds)"
                  >
                    <template v-if="timerState(current, index).running">
                      <v-icon size="18">
                        {{ $globals.icons.pause }}
                      </v-icon>
                      {{ $t("cook-mode.pause") }}
                    </template>
                    <template v-else>
                      <svg width="11" height="13" viewBox="0 0 11 13" aria-hidden="true"><path d="M1 1 L10 6.5 L1 12 Z" fill="currentColor" /></svg>
                      {{ timerState(current, index).started ? $t("cook-mode.resume") : $t("general.start") }}
                    </template>
                  </button>
                </div>
              </div>
            </template>
            <div v-else class="cook-stage__text cook-stage__text--md">
              {{ $t("cook-mode.no-steps") }}
            </div>
          </div>

          <nav class="cook-nav">
            <button
              type="button"
              class="cook-nav__btn"
              :disabled="current === 0"
              @click="previous"
            >
              <svg width="8" height="14" viewBox="0 0 12 20" aria-hidden="true"><polyline
                points="10,2 2,10 10,18"
                fill="none"
                stroke="currentColor"
                stroke-width="2.6"
                stroke-linecap="round"
                stroke-linejoin="round"
              /></svg>
              <span class="cook-nav__label">{{ $t("cook-mode.previous") }}</span>
            </button>
            <button
              type="button"
              class="cook-nav__btn cook-nav__btn--primary"
              @click="next"
            >
              {{ isLast ? $t("cook-mode.finish") : $t("cook-mode.next-step") }}
              <svg width="8" height="14" viewBox="0 0 8 14" aria-hidden="true"><polyline
                points="1.5,1.5 6.5,7 1.5,12.5"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
              /></svg>
            </button>
            <span class="cook-nav__hint">{{ $t("cook-mode.keyboard-hint") }}</span>
          </nav>
        </main>

        <!-- Side panel: every step, or the full ingredient list -->
        <aside
          class="cook-panel"
          :class="{ 'cook-panel--open': panelOpenOnSmall }"
        >
          <template v-if="panel === 'ingredients'">
            <div class="cook-panel__header">
              <span class="cook-panel__title">{{ $t("recipe.ingredients") }}</span>
              <RecipePageServingsStepper v-model="scale" :recipe="recipe" />
            </div>
            <RecipeIngredients
              class="cook-panel__ingredients"
              :value="recipe.recipeIngredient"
              :scale="scale"
              is-cook-mode
              :storage-key="ingredientStorageKey"
            />
          </template>
          <template v-else>
            <div class="cook-panel__header">
              <span class="cook-panel__title">{{ $t("cook-mode.all-steps") }}</span>
            </div>
            <ol class="cook-steps">
              <template v-for="(item, index) in stepList" :key="index">
                <li v-if="item.section" class="cook-steps__section">
                  {{ item.section }}
                </li>
                <li>
                  <button
                    type="button"
                    class="cook-steps__item"
                    :class="{
                      'cook-steps__item--current': index === current,
                      'cook-steps__item--done': index < current,
                    }"
                    :aria-current="index === current ? 'step' : undefined"
                    @click="goTo(index)"
                  >
                    <span class="cook-steps__num">
                      <svg v-if="index < current" width="14" height="11" viewBox="0 0 12 10" aria-hidden="true"><polyline
                        points="1.5,5 4.5,8 10.5,1.8"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      /></svg>
                      <template v-else>{{ index + 1 }}</template>
                    </span>
                    <span class="cook-steps__text">{{ item.text }}</span>
                  </button>
                </li>
              </template>
            </ol>
          </template>
        </aside>
      </div>

      <!-- Small screens: the side panel becomes a sheet, opened from here -->
      <button
        v-if="steps.length"
        type="button"
        class="cook-panel-toggle"
        @click="togglePanel('steps')"
      >
        <v-icon size="18">
          {{ panelOpenOnSmall && panel === 'steps' ? $globals.icons.close : $globals.icons.formatListBulleted }}
        </v-icon>
        <span class="cook-panel-toggle__label">
          {{ panelOpenOnSmall && panel === 'steps' ? $t("general.close") : $t("cook-mode.all-steps") }}
        </span>
      </button>
    </div>
  </v-theme-provider>
</template>

<script setup lang="ts">
import { onKeyStroke, useIntervalFn, useSessionStorage, useSwipe, useWakeLock } from "@vueuse/core";
import RecipePageServingsStepper from "./RecipePageServingsStepper.vue";
import RecipeIngredients from "~/components/Domain/Recipe/RecipeIngredients.vue";
import { useIngredientTextParser } from "~/composables/recipes";
import { useExtractIngredientReferences } from "~/composables/recipe-page/use-extract-ingredient-references";
import { highlightTerms, ingredientHighlightTerms } from "~/composables/recipe-page/use-cook-mode-highlights";
import { formatTimer, parseStepTimers } from "~/composables/recipe-page/use-step-timers";
import type { NoUndefinedField } from "~/lib/api/types/non-generated";
import type { Recipe, RecipeIngredient, RecipeNote } from "~/lib/api/types/recipe";

interface Props {
  recipe: NoUndefinedField<Recipe>;
  ingredientStorageKey?: string;
}
const props = withDefaults(defineProps<Props>(), {
  ingredientStorageKey: undefined,
});

const scale = defineModel<number>("scale", { default: 1 });

const emit = defineEmits<{
  exit: [];
}>();

const i18n = useI18n();
const display = useDisplay();
const { useParsedIngredientText } = useIngredientTextParser();
const { extractIngredientReferences } = useExtractIngredientReferences();

/* ---------- Steps ---------- */
const steps = computed(() => props.recipe.recipeInstructions || []);
const stepStorage = useSessionStorage<number>(`cook-mode:${props.recipe.id || props.recipe.slug}:step`, 0);
const current = computed({
  get: () => Math.min(Math.max(0, stepStorage.value), Math.max(0, steps.value.length - 1)),
  set: (value: number) => {
    stepStorage.value = value;
  },
});
const step = computed(() => steps.value[current.value]);
const isLast = computed(() => current.value >= steps.value.length - 1);

function plain(markdown: string | null | undefined) {
  return (markdown || "")
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
    .replace(/<[^>]+>/g, "")
    .replace(/[*_`#>]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

/** each step with the section heading that starts at it, as the recipe page groups them */
const stepList = computed(() =>
  steps.value.map(item => ({
    section: item.title?.trim() || "",
    text: plain(item.summary) || plain(item.text),
  })),
);

/** the section the current step sits in: the nearest heading at or before it */
const sectionTitle = computed(() => {
  for (let i = current.value; i >= 0; i--) {
    const title = steps.value[i]?.title?.trim();
    if (title) {
      return title;
    }
  }
  return "";
});

function goTo(index: number) {
  current.value = Math.min(Math.max(0, index), steps.value.length - 1);
  panelOpenOnSmall.value = false;
  stage.value?.querySelector(".cook-stage__scroll")?.scrollTo({ top: 0 });
}

function previous() {
  if (current.value > 0) {
    goTo(current.value - 1);
  }
}

function next() {
  if (isLast.value) {
    exit();
    return;
  }
  goTo(current.value + 1);
}

function exit() {
  emit("exit");
}

/* ---------- What the step uses ---------- */
const usedIngredients = computed<RecipeIngredient[]>(() => {
  const active = step.value;
  if (!active) {
    return [];
  }
  const ingredients = props.recipe.recipeIngredient || [];
  const linked = (active.ingredientReferences || [])
    .map(ref => ref.referenceId)
    .filter((id): id is string => !!id);
  // without links set up in the editor, find the ingredients the step's text mentions
  const ids = linked.length
    ? new Set(linked)
    : extractIngredientReferences(ingredients, [], plain(active.text));
  return ingredients.filter(ingredient => ingredient.referenceId && ids.has(ingredient.referenceId));
});

const uses = computed(() =>
  usedIngredients.value.map((ingredient) => {
    const parsed = useParsedIngredientText(ingredient, scale.value, true);
    const amount = [parsed.quantity, parsed.unit].filter(Boolean).join(" ");
    return {
      amount,
      name: parsed.name || parsed.note || "",
    };
  }).filter(use => use.name || use.amount),
);

const highlightedText = computed(() =>
  highlightTerms(step.value?.text || "", ingredientHighlightTerms(usedIngredients.value, step.value?.text || "")),
);

/** long steps step down a size or two so they still fit without scrolling */
const textSize = computed(() => {
  const length = plain(step.value?.text).length;
  if (length > 360) {
    return "sm";
  }
  if (length > 180) {
    return "md";
  }
  return "lg";
});

const notes = computed<RecipeNote[]>(() => {
  const ids = (step.value?.noteReferences || []).map(ref => ref.referenceId);
  if (!ids.length) {
    return [];
  }
  return (props.recipe.notes || []).filter(note => note.referenceId && ids.includes(note.referenceId));
});

const servings = computed(() => {
  const base = props.recipe.recipeServings || props.recipe.recipeYieldQuantity;
  return base ? Math.round(base * scale.value * 100) / 100 : 0;
});

const barMeta = computed(() => {
  const parts: string[] = [];
  if (steps.value.length) {
    parts.push(i18n.t("cook-mode.step-of-total", { step: current.value + 1, total: steps.value.length }));
  }
  if (servings.value) {
    parts.push(i18n.t("recipe.serves-amount", { amount: servings.value }));
  }
  return parts.join(" · ");
});

/* ---------- Timers ---------- */
interface TimerState {
  total: number;
  remaining: number;
  running: boolean;
  started: boolean;
  done: boolean;
  endsAt: number;
}

const stepTimers = computed(() => parseStepTimers(step.value?.text));
const timers = reactive<Record<string, TimerState>>({});

function timerKey(stepIndex: number, index: number) {
  return `${stepIndex}:${index}`;
}

function timerState(stepIndex: number, index: number): TimerState {
  const existing = timers[timerKey(stepIndex, index)];
  if (existing) {
    return existing;
  }
  const seconds = parseStepTimers(steps.value[stepIndex]?.text)[index]?.seconds ?? 0;
  return { total: seconds, remaining: seconds, running: false, started: false, done: false, endsAt: 0 };
}

function toggleTimer(stepIndex: number, index: number, seconds: number) {
  const key = timerKey(stepIndex, index);
  const timer = timers[key] ?? { total: seconds, remaining: seconds, running: false, started: false, done: false, endsAt: 0 };
  if (timer.running) {
    timer.remaining = Math.max(0, (timer.endsAt - Date.now()) / 1000);
    timer.running = false;
  }
  else {
    timer.endsAt = Date.now() + timer.remaining * 1000;
    timer.running = true;
    timer.started = true;
    unlockAudio();
  }
  timers[key] = timer;
}

function resetTimer(stepIndex: number, index: number) {
  // eslint-disable-next-line @typescript-eslint/no-dynamic-delete
  delete timers[timerKey(stepIndex, index)];
}

// timers count down from a wall-clock deadline, so a backgrounded tab doesn't fall behind
useIntervalFn(() => {
  const now = Date.now();
  for (const timer of Object.values(timers)) {
    if (!timer.running) {
      continue;
    }
    timer.remaining = Math.max(0, Math.ceil((timer.endsAt - now) / 1000));
    if (timer.remaining === 0) {
      timer.running = false;
      timer.done = true;
      chime();
    }
  }
}, 250);

const otherRunningTimers = computed(() =>
  Object.entries(timers)
    .map(([key, timer]) => ({ key, step: Number(key.split(":")[0]), ...timer }))
    .filter(timer => timer.step !== current.value && (timer.running || timer.done)),
);

let audio: AudioContext | null = null;

/** browsers only allow sound after a gesture, so the context is created when a timer starts */
function unlockAudio() {
  if (!audio && typeof AudioContext !== "undefined") {
    audio = new AudioContext();
  }
  audio?.resume();
}

function chime() {
  navigator.vibrate?.([200, 100, 200]);
  if (!audio) {
    return;
  }
  const start = audio.currentTime;
  [0, 0.35, 0.7].forEach((offset) => {
    const osc = audio!.createOscillator();
    const gain = audio!.createGain();
    osc.type = "sine";
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.0001, start + offset);
    gain.gain.exponentialRampToValueAtTime(0.3, start + offset + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + offset + 0.3);
    osc.connect(gain).connect(audio!.destination);
    osc.start(start + offset);
    osc.stop(start + offset + 0.32);
  });
}

/* ---------- Panel ---------- */
type Panel = "steps" | "ingredients";
const panel = ref<Panel>("steps");
const panelOpenOnSmall = ref(false);

function togglePanel(target: Panel) {
  if (display.mdAndDown.value) {
    const closing = panelOpenOnSmall.value && panel.value === target;
    panel.value = target;
    panelOpenOnSmall.value = !closing;
    return;
  }
  panel.value = panel.value === target ? "steps" : target;
}

/* ---------- Input ---------- */
function typingOrDialogOpen(e: KeyboardEvent) {
  const target = e.target as HTMLElement | null;
  if (target && (target.tagName === "INPUT" || target.tagName === "TEXTAREA" || target.isContentEditable)) {
    return true;
  }
  return !!document.querySelector(".v-overlay--active");
}

onKeyStroke("ArrowRight", (e) => {
  if (!typingOrDialogOpen(e)) {
    e.preventDefault();
    if (!isLast.value) {
      next();
    }
  }
});
onKeyStroke("ArrowLeft", (e) => {
  if (!typingOrDialogOpen(e)) {
    e.preventDefault();
    previous();
  }
});
onKeyStroke("Escape", (e) => {
  if (typingOrDialogOpen(e)) {
    return;
  }
  if (panelOpenOnSmall.value) {
    panelOpenOnSmall.value = false;
    return;
  }
  exit();
});

const stage = ref<HTMLElement | null>(null);
const { direction } = useSwipe(stage, {
  threshold: 60,
  onSwipeEnd() {
    if (direction.value === "left" && !isLast.value) {
      next();
    }
    else if (direction.value === "right") {
      previous();
    }
  },
});

/* ---------- Page ---------- */
// keep the screen on while cooking, and the page underneath from scrolling
const { isSupported: wakeLockSupported, request: requestWakeLock, release: releaseWakeLock } = useWakeLock();

onMounted(() => {
  document.documentElement.classList.add("cook-mode-open");
  if (wakeLockSupported.value) {
    requestWakeLock("screen").catch(() => {});
  }
});

onBeforeUnmount(() => {
  document.documentElement.classList.remove("cook-mode-open");
  if (wakeLockSupported.value) {
    releaseWakeLock().catch(() => {});
  }
  audio?.close();
});
</script>

<style scoped>
.cook-mode {
  --cook-bg: #121110;
  --cook-ink: #f5f3ef;
  --cook-muted: #9a978f;
  --cook-faint: #7d7a73;
  --cook-soft: #c9c5bd;
  --cook-fill: rgba(255, 255, 255, 0.1);
  --cook-fill-subtle: rgba(255, 255, 255, 0.08);
  --cook-hairline: rgba(255, 255, 255, 0.06);
  --cook-accent: rgb(var(--v-theme-primary));
  --cook-accent-text: #f0915f;

  position: fixed;
  inset: 0;
  /* keep the controls clear of the notch and home indicator; the background still fills the screen */
  padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
  box-sizing: border-box;
  /* under Vuetify's overlays (2000+), so menus and dialogs opened from here stay on top */
  z-index: 1999;
  display: flex;
  flex-direction: column;
  background: var(--cook-bg);
  color: var(--cook-ink);
  overflow: hidden;
}

/* ---------- Top bar ---------- */
.cook-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  height: 72px;
  flex-shrink: 0;
  padding: 0 40px;
  white-space: nowrap;
}

.cook-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 16px;
  border: 0;
  border-radius: 18px;
  background: var(--cook-fill);
  color: var(--cook-ink);
  font: inherit;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.cook-pill:hover {
  background: rgba(255, 255, 255, 0.14);
}

.cook-pill--active {
  background: rgba(224, 104, 60, 0.18);
  color: var(--cook-accent-text);
}

.cook-bar__title {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  min-width: 0;
}

.cook-bar__name {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 15px;
  font-weight: 600;
}

.cook-bar__meta {
  font-size: 13px;
  color: var(--cook-muted);
}

.cook-progress {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
  padding: 0 40px;
}

.cook-progress__segment {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: rgba(255, 255, 255, 0.14);
  transition: background-color 0.25s ease;
}

.cook-progress__segment--on {
  background: var(--cook-accent);
}

/* ---------- Body ---------- */
.cook-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 400px;
}

.cook-stage {
  display: flex;
  flex-direction: column;
  min-height: 0;
  touch-action: pan-y;
}

.cook-stage__scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 72px 80px 24px 120px;
}

.cook-running {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: -40px 0 24px;
}

.cook-running__timer {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 12px;
  border: 0;
  border-radius: 15px;
  background: var(--cook-fill-subtle);
  color: var(--cook-soft);
  font: inherit;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  cursor: pointer;
}

.cook-running__timer--done {
  background: rgba(224, 104, 60, 0.18);
  color: var(--cook-accent-text);
  animation: cook-pulse 1.2s ease-in-out infinite;
}

.cook-stage__eyebrow {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--cook-faint);
}

.cook-stage__text {
  max-width: 760px;
  margin-top: 16px;
  font-weight: 600;
  text-wrap: pretty;
  animation: cook-step-in 0.25s ease;
}

.cook-stage__text--lg {
  font-size: 52px;
  letter-spacing: -0.028em;
  line-height: 1.15;
}

.cook-stage__text--md {
  font-size: 38px;
  letter-spacing: -0.022em;
  line-height: 1.2;
}

.cook-stage__text--sm {
  font-size: 28px;
  letter-spacing: -0.015em;
  line-height: 1.3;
}

.cook-stage__text :deep(.cook-hl) {
  color: var(--cook-accent-text);
}

.cook-stage__text :deep(img) {
  max-width: 100%;
  border-radius: 18px;
  margin-top: 16px;
}

.cook-stage__text :deep(a) {
  color: inherit;
  text-decoration: underline;
  text-decoration-color: var(--cook-faint);
}

.cook-uses {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 32px;
}

.cook-uses__chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 18px;
  border-radius: 20px;
  background: var(--cook-fill-subtle);
  font-size: 17px;
}

.cook-uses__amount {
  font-weight: 600;
  white-space: nowrap;
}

.cook-uses__name {
  color: var(--cook-soft);
}

.cook-notes {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 760px;
  margin-top: 28px;
}

.cook-notes__note {
  padding: 16px 20px;
  border-radius: 18px;
  background: #1f1e1c;
  box-shadow: inset 0 0 0 1px var(--cook-hairline);
  color: var(--cook-soft);
  font-size: 16px;
  line-height: 1.45;
}

.cook-notes__title {
  margin-bottom: 4px;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--cook-muted);
}

.cook-timer {
  display: flex;
  align-items: center;
  gap: 40px;
  width: fit-content;
  margin-top: 36px;
  padding: 18px 18px 18px 26px;
  border-radius: 26px;
  background: #1f1e1c;
  box-shadow: inset 0 0 0 1px var(--cook-hairline);
  white-space: nowrap;
}

.cook-timer--done {
  box-shadow: inset 0 0 0 2px var(--cook-accent);
  animation: cook-pulse 1.2s ease-in-out infinite;
}

.cook-timer__readout {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cook-timer__label {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--cook-muted);
}

.cook-timer--done .cook-timer__label {
  color: var(--cook-accent-text);
}

.cook-timer__time {
  font-size: 56px;
  font-weight: 300;
  letter-spacing: -0.02em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.cook-timer__controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cook-timer__toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  height: 52px;
  padding: 0 26px;
  border: 0;
  border-radius: 26px;
  background: rgba(224, 104, 60, 0.18);
  color: var(--cook-accent-text);
  font: inherit;
  font-size: 17px;
  font-weight: 600;
  cursor: pointer;
}

.cook-timer__reset {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 52px;
  height: 52px;
  border: 0;
  border-radius: 26px;
  background: var(--cook-fill-subtle);
  color: var(--cook-soft);
  cursor: pointer;
}

.cook-nav {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
  padding: 16px 80px 44px 120px;
  white-space: nowrap;
}

.cook-nav__btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  height: 56px;
  padding: 0 24px;
  border: 0;
  border-radius: 28px;
  background: var(--cook-fill);
  color: var(--cook-ink);
  font: inherit;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.cook-nav__btn:disabled {
  opacity: 0.35;
  cursor: default;
}

.cook-nav__btn--primary {
  padding: 0 30px;
  background: var(--cook-accent);
  color: rgb(var(--v-theme-on-primary));
}

.cook-nav__hint {
  margin-left: 8px;
  font-size: 13px;
  color: var(--cook-faint);
}

.cook-pill:focus-visible,
.cook-nav__btn:focus-visible,
.cook-timer__toggle:focus-visible,
.cook-timer__reset:focus-visible,
.cook-steps__item:focus-visible,
.cook-running__timer:focus-visible,
.cook-panel-toggle:focus-visible {
  outline: 2px solid var(--cook-accent-text);
  outline-offset: 2px;
}

/* ---------- Side panel ---------- */
.cook-panel {
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-y: auto;
  padding: 40px 32px;
  border-left: 1px solid var(--cook-hairline);
  box-sizing: border-box;
}

.cook-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0 14px 10px;
}

.cook-panel__title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--cook-faint);
}

.cook-panel__ingredients {
  padding: 0 14px;
}

.cook-steps {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.cook-steps__section {
  padding: 14px 14px 4px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--cook-muted);
}

.cook-steps__item {
  display: flex;
  gap: 14px;
  width: 100%;
  padding: 12px 14px;
  border: 0;
  border-radius: 14px;
  background: transparent;
  color: var(--cook-soft);
  font: inherit;
  font-size: 14px;
  line-height: 1.4;
  text-align: left;
  cursor: pointer;
}

.cook-steps__item:hover {
  background: rgba(255, 255, 255, 0.04);
}

.cook-steps__item--current,
.cook-steps__item--current:hover {
  background: rgba(224, 104, 60, 0.14);
  color: var(--cook-ink);
}

.cook-steps__item--done {
  color: var(--cook-faint);
}

.cook-steps__num {
  width: 18px;
  flex-shrink: 0;
  font-weight: 600;
  color: var(--cook-muted);
}

.cook-steps__item--current .cook-steps__num {
  font-weight: 700;
  color: var(--cook-accent-text);
}

.cook-steps__item--done .cook-steps__num {
  color: var(--cook-faint);
}

.cook-steps__text {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  overflow: hidden;
}

.cook-panel-toggle {
  display: none;
}

@keyframes cook-step-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@keyframes cook-pulse {
  50% {
    opacity: 0.7;
  }
}

@media (prefers-reduced-motion: reduce) {
  .cook-stage__text,
  .cook-timer--done,
  .cook-running__timer--done {
    animation: none;
  }
}

/* ---------- Smaller screens ---------- */
@media (max-width: 1280px) {
  .cook-body {
    grid-template-columns: minmax(0, 1fr) 340px;
  }

  .cook-stage__scroll {
    padding: 56px 56px 24px 64px;
  }

  .cook-nav {
    padding: 16px 56px 36px 64px;
  }
}

@media (max-width: 1279.98px) {
  .cook-body {
    grid-template-columns: minmax(0, 1fr);
  }

  .cook-panel {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
    max-height: 75%;
    padding: 24px calc(16px + env(safe-area-inset-right)) calc(88px + env(safe-area-inset-bottom))
      calc(16px + env(safe-area-inset-left));
    border-left: 0;
    border-radius: 24px 24px 0 0;
    background: #1c1b19;
    box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.5);
    transform: translateY(100%);
    visibility: hidden;
    transition:
      transform 0.25s ease,
      visibility 0.25s;
  }

  .cook-panel--open {
    transform: none;
    visibility: visible;
  }

  .cook-panel-toggle {
    position: absolute;
    right: calc(24px + env(safe-area-inset-right));
    bottom: calc(36px + env(safe-area-inset-bottom));
    z-index: 2;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    height: 56px;
    padding: 0 22px;
    border: 0;
    border-radius: 28px;
    background: var(--cook-fill);
    color: var(--cook-ink);
    font: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
  }

  .cook-nav__hint {
    display: none;
  }
}

@media (max-width: 700px) {
  .cook-bar {
    height: 60px;
    padding: 0 16px;
  }

  .cook-progress {
    padding: 0 16px;
  }

  .cook-stage__scroll {
    padding: 32px 20px 16px;
  }

  .cook-running {
    margin: -12px 0 16px;
  }

  .cook-stage__text--lg {
    font-size: 32px;
  }

  .cook-stage__text--md {
    font-size: 26px;
  }

  .cook-stage__text--sm {
    font-size: 21px;
  }

  .cook-uses__chip {
    min-height: 36px;
    padding: 0 14px;
    font-size: 15px;
  }

  .cook-timer {
    gap: 20px;
    padding: 14px 14px 14px 20px;
  }

  .cook-timer__time {
    font-size: 40px;
  }

  .cook-timer__toggle {
    height: 46px;
    padding: 0 18px;
  }

  .cook-timer__reset {
    width: 46px;
    height: 46px;
  }

  .cook-nav {
    gap: 10px;
    /* clear of the steps button in the corner */
    padding: 12px 84px 24px 20px;
  }

  .cook-nav__label {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }

  .cook-nav__btn {
    height: 50px;
    padding: 0 18px;
  }

  .cook-nav__btn:not(.cook-nav__btn--primary) {
    width: 50px;
    padding: 0;
    justify-content: center;
  }

  .cook-nav__btn--primary {
    padding: 0 22px;
  }

  .cook-panel-toggle {
    right: calc(20px + env(safe-area-inset-right));
    bottom: calc(24px + env(safe-area-inset-bottom));
    width: 50px;
    height: 50px;
    padding: 0;
    justify-content: center;
  }

  .cook-panel-toggle__label {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0 0 0 0);
    white-space: nowrap;
  }
}
</style>

<style>
html.cook-mode-open {
  overflow: hidden !important;
}

html.cook-mode-open .v-app-bar {
  display: none !important;
}
</style>
