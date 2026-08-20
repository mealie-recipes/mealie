<template>
  <v-card variant="outlined" style="border-color: lightgrey;" class="d-flex flex-column mt-4 pa-2 w-100">
    <BaseDialog
      v-model="blockDialog"
      :title="$t('user.block-ip') || 'Block IP'"
      :icon="$globals.icons.alertCircle"
      color="error"
      can-confirm
      :submit-disabled="!pendingIp"
      @confirm="submitBlockIp"
    >
      <template #activator />
      <v-card-text>
        <p class="mb-3">
          {{ $t("general.are-you-sure") || "Are you sure?" }}
        </p>
        <v-text-field
          :model-value="pendingIp || ''"
          :label="$t('general.ip-address') || 'IP Address'"
          readonly
          variant="outlined"
          class="mb-3"
        />
        <v-textarea
          v-model="blockReason"
          :label="$t('general.reason') || 'Reason'"
          variant="outlined"
          rows="3"
          clearable
        />
      </v-card-text>
    </BaseDialog>
    <v-card-title class="text-subtitle-1">
      {{ $t("user.login-history") || "Login History" }}
    </v-card-title>

    <v-card-text class="pt-2">
      <AppLoader v-if="loading" :loading="loading" :waiting-text="$t('general.loading') || 'Loading...'" />

      <v-alert v-else-if="errorMessage" type="error" variant="tonal" class="mb-3">
        {{ errorMessage }}
      </v-alert>

      <v-alert v-else-if="items.length === 0" type="info" variant="tonal">
        {{ $t("general.no-results") || "No login history yet." }}
      </v-alert>

      <v-data-table
        v-else
        :headers="headers"
        :items="items"
        :items-per-page="perPage"
        item-key="id"
        class="elevation-0 w-100"
      >
        <template #[`item.success`]="{ item }">
          <v-chip size="small" :color="item.success ? 'success' : 'error'" variant="flat">
            {{ item.success ? ($t("general.success") || "Success") : ($t("general.failed") || "Failed") }}
          </v-chip>
        </template>

        <template #[`item.authMethod`]="{ item }">
          <v-chip size="small" variant="tonal">
            {{ item.authMethod || "-" }}
          </v-chip>
        </template>
        <template #[`item.username`]="{ item }">
          <span class="username-cell" :title="item.username || '-'">
            {{ truncateUsername(item.username) }}
          </span>
        </template>

        <template #[`item.createdAt`]="{ item }">
          {{ formatDate(item.createdAt) }}
        </template>

        <template #[`item.reason`]="{ item }">
          {{ item.reason || "-" }}
        </template>

        <template #[`item.ipAddress`]="{ item }">
          {{ item.ipAddress || "-" }}
          <v-chip v-if="item.isBlocked">
            this ip is blocked.
            <v-btn size="x-small" color="pass" variant="tonal" class="ml-2" @click="unBlock(item.ipAddress)">
              unblock this ip
            </v-btn>
          </v-chip>
          <v-chip v-else>
            <v-btn
              size="x-small"
              color="error"
              variant="tonal"
              class="ml-2"
              :disabled="!item.ipAddress"
              @click="openBlockDialog(item.ipAddress)"
            >
              Block this IP
            </v-btn>
          </v-chip>
        </template>

        <template #[`item.userAgent`]="{ item }">
          <span class="text-caption">{{ item.userAgent || "-" }}</span>
        </template>
      </v-data-table>

      <div v-if="totalPages > 1" class="d-flex justify-end mt-3">
        <v-pagination v-model="page" :length="totalPages" density="comfortable" @update:model-value="loadHistory" />
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { useUserApi } from "~/composables/api";
import type { PaginationData } from "~/lib/api/types/non-generated";

const { userId } = defineProps<{ userId?: string }>();

interface LoginHistoryItem {
  id: string;
  userId?: string | null;
  username?: string | null;
  authMethod?: "MEALIE" | "LDAP" | "OIDC" | null;
  success: boolean;
  reason?: string | null;
  ipAddress?: string | null;
  isBlocked: boolean;
  userAgent?: string | null;
  createdAt?: string | null;
}

const i18n = useI18n();
const api = useUserApi();

const loading = ref(false);
const errorMessage = ref("");
const items = ref<LoginHistoryItem[]>([]);

const page = ref(1);
const perPage = 15;
const totalPages = ref(1);
const maxUsernameLength = 10;

const headers = computed(() => [
  { title: i18n.t("general.date") || "Date", value: "createdAt" },
  { title: i18n.t("user.username") || "Username", value: "username" },
  { title: i18n.t("general.status") || "Status", value: "success" },
  { title: i18n.t("user.auth-method") || "Auth Method", value: "authMethod" },
  { title: i18n.t("general.reason") || "Reason", value: "reason" },
  { title: "IP", value: "ipAddress" },
  { title: "User Agent", value: "userAgent" },
]);

function normalizeItem(raw: Record<string, any>): LoginHistoryItem {
  return {
    id: raw.id,
    userId: raw.userId ?? raw.user_id ?? null,
    username: raw.username ?? raw.username ?? null,
    authMethod: raw.authMethod ?? raw.auth_method ?? null,
    success: Boolean(raw.success),
    reason: raw.reason ?? null,
    ipAddress: raw.ipAddress ?? raw.ip_address ?? null,
    isBlocked: Boolean(raw.isBlocked),
    userAgent: raw.userAgent ?? raw.user_agent ?? null,
    createdAt: raw.createdAt ?? raw.created_at ?? null,
  };
}

function formatDate(value?: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function truncateUsername(value?: string | null) {
  if (!value) return "-";
  if (value.length <= maxUsernameLength) return value;
  return `${value.slice(0, maxUsernameLength)}...`;
}
const { $globals } = useNuxtApp();

const blockDialog = ref(false);
const pendingIp = ref<string | null>(null);
const blockReason = ref("");

const auth = useMealieAuth();
const effectiveUserId = computed(() => userId || auth.user.value?.id || null);
async function unBlock(ip?: string | null) {
  if (!ip) return;

  const { data, error } = await api.users.requests.post(
    "/api/users/self/remove-ip-blocklist",
    {
      ip_address: ip,
      user_id: effectiveUserId.value,
    },
  );

  if (error || !data) {
    errorMessage.value = i18n.t("general.error") || "Failed to unblock this ip.";
    return;
  }

  await loadHistory();
}
function openBlockDialog(ip?: string | null) {
  if (!ip) return;
  pendingIp.value = ip;
  blockReason.value = "";
  blockDialog.value = true;
}

async function submitBlockIp() {
  if (!pendingIp.value) return;
  const { data, error } = await api.users.requests.post("/api/users/self/ip-blocklist",
    {
      user_id: effectiveUserId.value,
      ip_address: pendingIp.value,
      reason: blockReason.value || null,
    });

  if (error || !data) {
    errorMessage.value = i18n.t("general.error") || "Failed to block this ip.";
    return;
  }
  blockDialog.value = false;
  pendingIp.value = null;
  blockReason.value = "";
  await loadHistory();
}

async function loadHistory() {
  loading.value = true;
  errorMessage.value = "";

  const { data, error } = await api.users.requests.get<PaginationData<Record<string, any>>>(
    "/api/users/getLoginHistory",
    {
      userId: effectiveUserId.value,
      page: page.value,
      perPage,
    },
  );

  if (error || !data) {
    errorMessage.value = i18n.t("general.error") || "Failed to load login history.";
    loading.value = false;
    return;
  }

  items.value = (data.items || []).map(normalizeItem);
  totalPages.value = data.total_pages || 1;
  loading.value = false;
}

onMounted(loadHistory);
</script>

<style scoped>
.username-cell {
  display: inline-block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: bottom;
}
</style>
