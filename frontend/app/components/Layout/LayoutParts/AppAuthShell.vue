<template>
  <div class="auth-shell">
    <div class="auth-shell__column" :class="{ 'auth-shell__column--wide': wide }">
      <div class="auth-shell__brand">
        <span class="auth-shell__mark">M</span>
        <span class="auth-shell__name">Mealie</span>
      </div>

      <slot name="above" />

      <section class="auth-shell__card">
        <h1 v-if="title" class="auth-shell__title">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="auth-shell__subtitle">
          {{ subtitle }}
        </p>
        <slot />
      </section>

      <div v-if="$slots.footer" class="auth-shell__footer">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    default: "",
  },
  subtitle: {
    type: String,
    default: "",
  },
  /** room for multi-column content, such as the registration steps */
  wide: {
    type: Boolean,
    default: false,
  },
});
</script>

<style scoped>
.auth-shell {
  display: flex;
  justify-content: center;
  min-height: 100vh;
  padding: 64px 16px 48px;
  box-sizing: border-box;
  background:
    radial-gradient(1200px 600px at 50% -10%, rgba(var(--v-theme-primary), 0.08), transparent 70%), var(--mealie-canvas);
  color: var(--mealie-ink);
}

.auth-shell__column {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 20px;
  width: 100%;
  max-width: 420px;
}

.auth-shell__column--wide {
  max-width: 720px;
}

.auth-shell__brand {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  margin-bottom: 4px;
}

.auth-shell__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgb(var(--v-theme-primary));
  box-shadow: 0 12px 28px rgba(var(--v-theme-primary), 0.3);
  color: #fff;
  font-size: 28px;
  font-weight: 700;
}

.auth-shell__name {
  font-size: 22px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.auth-shell__card {
  padding: 28px 28px 24px;
  border-radius: 24px;
  background: var(--mealie-surface);
  box-shadow:
    inset 0 0 0 1px var(--mealie-hairline),
    0 30px 60px -40px rgba(40, 30, 20, 0.35);
}

.auth-shell__title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  text-align: center;
}

.auth-shell__subtitle {
  margin: 6px 0 0;
  font-size: 15px;
  line-height: 1.45;
  text-align: center;
  color: var(--mealie-text-secondary);
}

.auth-shell__footer {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 4px 12px;
  font-size: 13px;
  color: var(--mealie-text-tertiary);
}

@media (max-width: 600px) {
  .auth-shell {
    padding: 40px 12px 32px;
  }

  .auth-shell__card {
    padding: 22px 18px 18px;
  }
}
</style>

<style>
/* Fields, buttons and links inside the shell, matched to the rest of the redesign */
.auth-shell .v-field--variant-solo-filled,
.auth-shell .v-field--variant-filled {
  border-radius: 12px !important;
  background: var(--mealie-fill-subtle) !important;
  box-shadow: none !important;
}

.auth-shell .v-field--variant-filled .v-field__outline::before,
.auth-shell .v-field--variant-filled .v-field__outline::after {
  border-color: transparent !important;
}

.auth-shell .v-field--variant-solo-filled.v-field--focused,
.auth-shell .v-field--variant-filled.v-field--focused {
  box-shadow: 0 0 0 2px rgba(var(--v-theme-primary), 0.45) !important;
}

.auth-shell .v-field__overlay {
  opacity: 0 !important;
}

.auth-shell .v-btn.bg-primary,
.auth-shell .v-btn.bg-success {
  border-radius: 999px !important;
  background: rgb(var(--v-theme-primary)) !important;
  color: #fff !important;
  box-shadow: 0 8px 20px rgba(var(--v-theme-primary), 0.25) !important;
  font-weight: 600;
  letter-spacing: 0;
}

/* BaseButton turns tonal while disabled, which would otherwise bring back its green */
.auth-shell .v-btn--variant-tonal.text-success,
.auth-shell .v-btn--variant-tonal.text-primary {
  background: rgba(var(--v-theme-primary), 0.14) !important;
  color: rgb(var(--v-theme-primary)) !important;
}

.auth-shell .v-btn--variant-text,
.auth-shell .v-btn--variant-tonal {
  border-radius: 999px !important;
  letter-spacing: 0;
}

.auth-shell .v-btn.bg-grey {
  border-radius: 999px !important;
  background: var(--mealie-fill) !important;
  color: var(--mealie-ink) !important;
  box-shadow: none !important;
}
</style>
