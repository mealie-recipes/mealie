<template>
  <div>
    <BaseDialog
      v-model="dialog"
      bottom-sheet
      :title="$t('recipe-share.share-recipe')"
      :icon="$globals.icons.link"
    >
      <v-card-text
        v-if="qrCodeToken"
        class="d-flex flex-column align-center"
      >
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div class="qr-code" v-html="qrCodeSvg" />
        <p class="text-center text-medium-emphasis mt-3">
          {{ $t("recipe-share.scan-qr-code") }}
        </p>
        <div class="d-flex mt-4" style="gap: 8px;">
          <v-btn
            variant="text"
            :prepend-icon="$globals.icons.back"
            @click="qrCodeToken = null"
          >
            {{ $t("general.back") }}
          </v-btn>
          <v-btn
            variant="text"
            color="info"
            :prepend-icon="$globals.icons.download"
            @click="downloadQrCode"
          >
            {{ $t("general.download") }}
          </v-btn>
        </div>
      </v-card-text>
      <template v-else>
        <v-card-text>
          <v-menu
            v-model="datePickerMenu"
            :close-on-content-click="false"
            transition="scale-transition"
            offset-y
            max-width="290px"
            min-width="auto"
          >
            <template #activator="{ props: activatorProps }">
              <v-text-field
                :model-value="$d(expirationDate)"
                :label="$t('recipe-share.expiration-date')"
                :hint="$t('recipe-share.default-30-days')"
                persistent-hint
                :prepend-icon="$globals.icons.calendar"
                v-bind="activatorProps"
                readonly
              />
            </template>
            <v-date-picker
              v-model="expirationDate"
              hide-header
              :first-day-of-week="firstDayOfWeek"
              :local="$i18n.locale"
              @update:model-value="datePickerMenu = false"
            />
          </v-menu>
        </v-card-text>
        <v-card-actions class="justify-end">
          <BaseButton
            size="small"
            @click="createNewToken"
          >
            {{ $t("general.new") }}
          </BaseButton>
        </v-card-actions>

        <v-list-item
          v-for="token in tokens"
          :key="token.id"
          class="px-2"
          style="padding-top: 8px; padding-bottom: 8px;"
          @click="shareRecipe(token.id)"
        >
          <div class="d-flex align-center" style="width: 100%;">
            <v-avatar color="grey">
              <v-icon>
                {{ $globals.icons.link }}
              </v-icon>
            </v-avatar>

            <div
              class="pl-3 flex-grow-1"
              style="min-width: 0;"
            >
              <v-list-item-title class="text-wrap">
                {{ $t("recipe-share.expires-at") + ' ' + $d(new Date(token.expiresAt!)) }}
              </v-list-item-title>
            </div>

            <v-btn
              icon
              variant="text"
              class="ml-2"
              @click.stop="deleteToken(token.id)"
            >
              <v-icon color="error-lighten-1">
                {{ $globals.icons.delete }}
              </v-icon>
            </v-btn>
            <v-btn
              icon
              variant="text"
              class="ml-2"
              @click.stop="copyTokenLink(token.id)"
            >
              <v-icon color="info-lighten-1">
                {{ $globals.icons.contentCopy }}
              </v-icon>
            </v-btn>
            <v-btn
              icon
              variant="text"
              class="ml-2"
              :aria-label="$t('recipe-share.show-qr-code')"
              @click.stop="qrCodeToken = token.id"
            >
              <v-icon color="info-lighten-1">
                {{ $globals.icons.qrCode }}
              </v-icon>
            </v-btn>
          </div>
        </v-list-item>
      </template>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { useClipboard, useShare, whenever } from "@vueuse/core";
import { renderSVG } from "uqr";
import type { RecipeShareToken } from "~/lib/api/types/recipe";
import { useUserApi } from "~/composables/api";
import { useHouseholdSelf } from "~/composables/use-households";
import { alert } from "~/composables/use-toast";

interface Props {
  recipeId: string;
  name: string;
}
const props = defineProps<Props>();

const dialog = defineModel<boolean>({ default: false });

const datePickerMenu = ref(false);
const expirationDate = ref(new Date(Date.now() - new Date().getTimezoneOffset() * 60000));
const tokens = ref<RecipeShareToken[]>([]);
const qrCodeToken = ref<string | null>(null);

whenever(
  () => dialog.value,
  () => {
    // Set expiration date to today + 30 Days
    const today = new Date();
    expirationDate.value = new Date(today.getTime() + 30 * 24 * 60 * 60 * 1000);
    qrCodeToken.value = null;
    refreshTokens();
  },
);

const i18n = useI18n();
const auth = useMealieAuth();
const { household } = useHouseholdSelf();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

const firstDayOfWeek = computed(() => {
  return household.value?.preferences?.firstDayOfWeek || 0;
});

// ============================================================
// Token Actions

const userApi = useUserApi();

async function createNewToken() {
  // Convert expiration date to timestamp
  const { data } = await userApi.recipes.share.createOne({
    recipeId: props.recipeId,
    expiresAt: expirationDate.value.toISOString(),
  });

  if (data) {
    tokens.value.push(data);
  }
}

async function deleteToken(id: string) {
  await userApi.recipes.share.deleteOne(id);
  tokens.value = tokens.value.filter(token => token.id !== id);
}

async function refreshTokens() {
  const { data } = await userApi.recipes.share.getAll(1, -1, { recipe_id: props.recipeId });

  if (data) {
    // @ts-expect-error - TODO: This routes doesn't have pagination, but the type are mismatched.
    tokens.value = data ?? [];
  }
}

const { share, isSupported: shareIsSupported } = useShare();
const { copy, copied, isSupported } = useClipboard();

function getTokenLink(token: string) {
  return `${window.location.origin}/g/${groupSlug.value}/shared/r/${token}`;
}

async function copyTokenLink(token: string) {
  if (isSupported.value) {
    await copy(getTokenLink(token));
    if (copied.value) {
      alert.success(i18n.t("recipe-share.recipe-link-copied-message") as string);
    }
    else {
      alert.error(i18n.t("general.clipboard-copy-failure") as string);
    }
  }
  else {
    alert.error(i18n.t("general.clipboard-not-supported") as string);
  }
}

async function shareRecipe(token: string) {
  if (shareIsSupported.value) {
    share({
      title: props.name,
      url: getTokenLink(token),
    });
  }
  else {
    await copyTokenLink(token);
  }
}

// ============================================================
// QR Code

const qrCodeSvg = computed(() => qrCodeToken.value ? renderSVG(getTokenLink(qrCodeToken.value)) : "");

async function downloadQrCode() {
  // Rasterize the SVG so the download opens in any photo viewer
  const image = new Image();
  image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(qrCodeSvg.value)}`;
  await image.decode();

  const size = 1024;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const context = canvas.getContext("2d");
  if (!context) {
    return;
  }
  context.imageSmoothingEnabled = false;
  context.drawImage(image, 0, 0, size, size);

  const a = document.createElement("a");
  a.download = `${props.name}.png`;
  a.href = canvas.toDataURL("image/png");
  a.click();
}
</script>

<style scoped>
.qr-code {
  width: 100%;
  max-width: 320px;
}

.qr-code :deep(svg) {
  display: block;
  width: 100%;
  height: auto;
}
</style>
