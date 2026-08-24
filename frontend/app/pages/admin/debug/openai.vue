<template>
  <v-container class="pa-0">
    <v-container>
      <BaseCardSectionTitle :title="$t('admin.debug-openai-services')">
        {{ $t('admin.debug-openai-services-description') }}
        <br>
        <DocLink
          class="mt-2"
          link="/documentation/getting-started/installation/ai-providers"
        />
      </BaseCardSectionTitle>
    </v-container>
    <v-form
      ref="uploadForm"
      @submit.prevent="testOpenAI"
    >
      <div>
        <v-card-text>
          <v-container class="pa-0">
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-if="groups"
                  v-model="selectedGroupId"
                  :items="groups"
                  item-title="name"
                  item-value="id"
                  :label="$t('group.group')"
                  density="compact"
                  variant="outlined"
                  clearable
                  hide-details
                />
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  v-model="selectedProviderId"
                  :items="groupProviders"
                  item-title="name"
                  item-value="id"
                  :label="$t('group.ai-provider-settings.ai-provider')"
                  density="compact"
                  variant="outlined"
                  clearable
                  hide-details
                  :disabled="!selectedGroupId"
                />
              </v-col>
            </v-row>
            <v-row>
              <v-col
                cols="auto"
                align-self="center"
              >
                <AppButtonUpload
                  v-if="!uploadedImage"
                  class="ml-auto"
                  url="none"
                  file-name="image"
                  accept="image/*"
                  :text="$t('recipe.upload-image')"
                  :text-btn="false"
                  :post="false"
                  @uploaded="uploadImage"
                />
                <v-btn
                  v-if="!!uploadedImage"
                  color="error"
                  @click="clearImage"
                >
                  <v-icon start>
                    {{ $globals.icons.close }}
                  </v-icon>
                  {{ $t("recipe.remove-image") }}
                </v-btn>
              </v-col>
              <v-spacer />
            </v-row>
            <v-row
              v-if="uploadedImage && uploadedImagePreviewUrl"
              style="max-width: 25%;"
            >
              <v-spacer />
              <v-col cols="12">
                <v-img :src="uploadedImagePreviewUrl" />
              </v-col>
              <v-spacer />
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <BaseButton
            type="submit"
            :disabled="!selectedProviderId"
            :text="$t('admin.run-test')"
            :icon="$globals.icons.check"
            :loading="loading"
            class="ml-auto"
          />
        </v-card-actions>
      </div>
    </v-form>
    <v-divider
      v-if="response"
      class="mt-4"
    />
    <v-container
      v-if="response"
      class="ma-0 pa-0"
    >
      <v-card-title> {{ $t('admin.test-results') }} </v-card-title>
      <v-card-text> {{ response }} </v-card-text>
    </v-container>
  </v-container>
</template>

<script setup lang="ts">
import { useAdminApi } from "~/composables/api";
import { useGroups } from "~/composables/use-groups";
import { alert } from "~/composables/use-toast";
import type { AIProviderSummary } from "~/lib/api/types/group";

definePageMeta({
  layout: "admin",
});

const api = useAdminApi();
const i18n = useI18n();

// Set page title
useSeoMeta({
  title: i18n.t("admin.debug-openai-services"),
});

const loading = ref(false);
const response = ref("");

const uploadedImage = ref<Blob | File>();
const uploadedImageName = ref<string>("");
const uploadedImagePreviewUrl = ref<string>();

// Group + provider selection
const { groups } = useGroups();
const selectedGroupId = ref<string | null>(null);
const groupProviders = ref<AIProviderSummary[]>([]);
const selectedProviderId = ref<string | null>(null);

watch(selectedGroupId, (id) => {
  groupProviders.value = [];
  selectedProviderId.value = null;
  if (!id) return;
  const group = groups.value?.find(g => g.id === id);
  groupProviders.value = group?.aiProviderSettings?.providers ?? [];
});

function uploadImage(fileObject: unknown) {
  uploadedImage.value = fileObject as File;
  uploadedImageName.value = (fileObject as File).name;
  uploadedImagePreviewUrl.value = URL.createObjectURL(fileObject as File);
}

function clearImage() {
  uploadedImage.value = undefined;
  uploadedImageName.value = "";
  uploadedImagePreviewUrl.value = undefined;
}

async function testOpenAI() {
  if (!selectedProviderId.value) {
    alert.error("Please select a provider");
    return;
  }

  response.value = "";

  loading.value = true;
  const { data } = await api.debug.debugOpenAI(selectedProviderId.value, uploadedImage.value);
  loading.value = false;

  if (!data) {
    alert.error("Unable to test OpenAI services");
  }
  else {
    response.value = data.response || (data.success ? "Test Successful" : "Test Failed");
  }
}
</script>
