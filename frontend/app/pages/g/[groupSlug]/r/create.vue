<template>
  <div class="mealie-page create-page">
    <header class="mealie-page__header">
      <div class="mealie-page__titles">
        <div class="mealie-eyebrow">
          {{ $t("recipe-create.eyebrow") }}
        </div>
        <h1 class="mealie-page__title">
          {{ $t("recipe.recipe-creation") }}
        </h1>
      </div>
    </header>

    <nav class="create-methods" :aria-label="$t('recipe-create.how')">
      <RouterLink
        v-for="method in methods"
        :key="method.value"
        :to="{ path: `/g/${groupSlug}/r/create/${method.value}`, query: route.query }"
        class="create-method"
        :class="{ 'create-method--active': method.value === subpage }"
        :aria-current="method.value === subpage ? 'page' : undefined"
      >
        <span class="create-method__icon">
          <v-icon size="20">{{ method.icon }}</v-icon>
        </span>
        <span class="create-method__text">
          <span class="create-method__title">{{ method.title }}</span>
          <span class="create-method__desc">{{ method.description }}</span>
        </span>
      </RouterLink>
    </nav>

    <section class="create-panel mealie-card">
      <NuxtPage />
    </section>

    <AdvancedOnly>
      <div class="create-footer">
        <router-link
          :to="`/group/migrations`"
          class="text-primary"
        >
          {{ $t('recipe.looking-for-migrations') }}
        </router-link>
      </div>
    </AdvancedOnly>
  </div>
</template>

<script setup lang="ts">
import AdvancedOnly from "~/components/global/AdvancedOnly.vue";
import { useGroupSelf } from "~/composables/use-groups";

definePageMeta({
  middleware: ["auth", "group-only"],
});

const i18n = useI18n();
const auth = useMealieAuth();
const { $globals } = useNuxtApp();
const { group } = useGroupSelf();

useSeoMeta({
  title: i18n.t("general.create"),
});

interface CreateMethod {
  value: string;
  icon: string;
  title: string;
  description: string;
  hide?: boolean;
}

const methods = computed<CreateMethod[]>(() => ([
  { value: "url", icon: $globals.icons.link, title: i18n.t("recipe-create.url"), description: i18n.t("recipe-create.url-desc") },
  {
    value: "ai",
    icon: $globals.icons.autoFix,
    title: i18n.t("recipe-create.ai"),
    description: i18n.t("recipe-create.ai-desc"),
    hide: !group.value?.aiProviderSettings?.aiEnabled,
  },
  { value: "new", icon: $globals.icons.edit, title: i18n.t("recipe-create.new"), description: i18n.t("recipe-create.new-desc") },
  { value: "bulk", icon: $globals.icons.linkVariantPlus, title: i18n.t("recipe-create.bulk"), description: i18n.t("recipe-create.bulk-desc") },
  { value: "html", icon: $globals.icons.codeTags, title: i18n.t("recipe-create.html"), description: i18n.t("recipe-create.html-desc") },
  { value: "zip", icon: $globals.icons.zip, title: i18n.t("recipe-create.zip"), description: i18n.t("recipe-create.zip-desc") },
  { value: "debug", icon: $globals.icons.robot, title: i18n.t("recipe-create.debug"), description: i18n.t("recipe-create.debug-desc") },
] as CreateMethod[]).filter(method => !method.hide));

const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug || auth.user.value?.groupSlug || "");

const subpage = computed(() => route.path.split("/").pop() ?? "url");
</script>

<style scoped>
.create-methods {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 28px;
}

.create-method {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  background: var(--mealie-surface);
  box-shadow: inset 0 0 0 1px var(--mealie-hairline);
  color: var(--mealie-ink);
  text-decoration: none;
  transition:
    box-shadow 0.15s ease,
    background-color 0.15s ease;
}

.create-method:hover {
  box-shadow:
    inset 0 0 0 1px var(--mealie-hairline-strong),
    0 10px 24px -18px rgba(40, 30, 20, 0.4);
}

.create-method:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.create-method--active,
.create-method--active:hover {
  background: rgba(var(--v-theme-primary), 0.08);
  box-shadow: inset 0 0 0 2px rgb(var(--v-theme-primary));
}

.create-method__icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 10px;
  background: var(--mealie-fill-subtle);
  color: var(--mealie-icon);
}

.create-method--active .create-method__icon {
  background: rgb(var(--v-theme-primary));
  color: #fff;
}

.create-method__text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.create-method__title {
  font-size: 15px;
  font-weight: 600;
}

.create-method__desc {
  font-size: 13px;
  line-height: 1.35;
  color: var(--mealie-text-tertiary);
}

.create-panel {
  margin-top: 20px;
  padding: 20px 16px 16px;
}

.create-footer {
  margin-top: 24px;
  text-align: center;
}

@media (max-width: 600px) {
  .create-methods {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }

  .create-method {
    padding: 12px;
  }

  .create-method__desc {
    display: none;
  }
}
</style>

<style>
/* The importer subpages share one shape: a headline, some text, filled fields and a
   submit button. Restyled here once rather than in each of them. */
.create-panel .v-card-title.headline {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--mealie-ink);
  white-space: normal;
}

.create-panel .v-card-text {
  font-size: 15px;
  line-height: 1.5;
  color: var(--mealie-text-secondary);
}

.create-panel .v-field--variant-solo-filled,
.create-panel .v-field--variant-solo {
  border-radius: 12px !important;
  background: var(--mealie-fill-subtle) !important;
  box-shadow: none !important;
}

.create-panel .v-field--variant-solo-filled.v-field--focused,
.create-panel .v-field--variant-solo.v-field--focused {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.45) !important;
}

.create-panel .v-field--variant-solo-filled .v-field__overlay {
  opacity: 0 !important;
}

/* the submit buttons: the page's primary pill */
.create-panel .v-btn.bg-success {
  background: rgb(var(--v-theme-primary)) !important;
  color: #fff !important;
  border-radius: 999px !important;
  box-shadow: 0 8px 20px rgba(var(--v-theme-primary), 0.25) !important;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0;
}

/* BaseButton swaps to a tonal variant while disabled, which would bring the green back */
.create-panel .v-btn--variant-tonal.text-success {
  background: rgba(var(--v-theme-primary), 0.14) !important;
  color: rgb(var(--v-theme-primary)) !important;
  border-radius: 999px !important;
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0;
}

.create-panel .v-btn.bg-info,
.create-panel .v-btn.bg-error,
.create-panel .v-btn--icon.v-btn--variant-elevated {
  box-shadow: none !important;
}

.create-panel .v-btn.bg-info,
.create-panel .v-btn.bg-error {
  border-radius: 999px !important;
}
</style>
