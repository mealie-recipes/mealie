<template>
  <v-container fluid>
    <BaseDialog
      v-model="createDialog"
      :title="$t('household.create-household')"
      :icon="$globals.icons.household"
    >
      <template #activator> </template>
      <v-card-text>
        <v-form ref="refNewHouseholdForm">
          <v-select
            v-if="groups"
            v-model="createHouseholdForm.data.groupId"
            :items="groups"
            rounded
            class="rounded-lg"
            item-text="name"
            item-value="id"
            :return-object="false"
            filled
            :label="$tc('household.household-group')"
            :rules="[validators.required]"
          />
          <AutoForm v-model="createHouseholdForm.data" :update-mode="updateMode" :items="createHouseholdForm.items" />
        </v-form>
      </v-card-text>
      <template #custom-card-action>
        <BaseButton type="submit" @click="handleCreateSubmit"> {{ $t("general.create") }} </BaseButton>
      </template>
    </BaseDialog>

    <BaseDialog
      v-model="confirmDialog"
      :title="$t('general.confirm')"
      color="error"
      @confirm="deleteHousehold(deleteTarget)"
    >
      <template #activator> </template>
      <v-card-text>
        {{ $t("general.confirm-delete-generic") }}
      </v-card-text>
    </BaseDialog>

    <BaseCardSectionTitle :title="$tc('household.household-management')"> </BaseCardSectionTitle>
    <section>
      <v-toolbar flat color="transparent" class="justify-between">
        <BaseButton @click="openDialog"> {{ $t("general.create") }} </BaseButton>
      </v-toolbar>

      <v-data-table
        :headers="headers"
        :items="households || []"
        item-key="id"
        class="elevation-0"
        hide-default-footer
        disable-pagination
        :search="search"
        @click:row="handleRowClick"
      >
        <template #item.users="{ item }">
          {{ item.users.length }}
        </template>
        <template #item.group="{ item }">
          {{ item.group }}
        </template>
        <template #item.webhookEnable="{ item }">
          {{ item.webhooks.length > 0 ? $t("general.yes") : $t("general.no") }}
        </template>
        <template #item.actions="{ item }">
          <v-tooltip bottom :disabled="!(item && item.users.length > 0)">
            <template #activator="{ on, attrs }">
              <div v-bind="attrs" v-on="on" >
                <v-btn
                  :disabled="item && item.users.length > 0"
                  class="mr-1"
                  icon
                  color="error"
                  @click.stop="
                    confirmDialog = true;
                    deleteTarget = item.id;
                  "
                >
                  <v-icon>
                    {{ $globals.icons.delete }}
                  </v-icon>
                </v-btn>
              </div>
            </template>
            <span>{{ $tc("admin.household-delete-note") }}</span>
          </v-tooltip>
        </template>
      </v-data-table>
      <v-divider></v-divider>
    </section>
  </v-container>
</template>

<script lang="ts">
import { defineComponent, reactive, ref, toRefs, useContext, useRouter } from "@nuxtjs/composition-api";
import { fieldTypes } from "~/composables/forms";
import { useGroups } from "~/composables/use-groups";
import { useAdminHouseholds } from "~/composables/use-households";
import { validators } from "~/composables/use-validators";
import { HouseholdInDB } from "~/lib/api/types/household";
import { VForm } from "~/types/vuetify";

export default defineComponent({
  layout: "admin",
  setup() {
    const { i18n } = useContext();
    const { groups } = useGroups();
    const { households, refreshAllHouseholds, deleteHousehold, createHousehold } = useAdminHouseholds();
    const refNewHouseholdForm = ref<VForm | null>(null);

    const state = reactive({
      createDialog: false,
      confirmDialog: false,
      loading: false,
      deleteTarget: 0,
      search: "",
      headers: [
        {
          text: i18n.t("household.household"),
          align: "start",
          sortable: false,
          value: "id",
        },
        { text: i18n.t("general.name"), value: "name" },
        { text: i18n.t("group.group"), value: "group" },
        { text: i18n.t("user.total-users"), value: "users" },
        { text: i18n.t("user.webhooks-enabled"), value: "webhookEnable" },
        { text: i18n.t("general.delete"), value: "actions" },
      ],
      updateMode: false,
      createHouseholdForm: {
        items: [
          {
            label: i18n.t("household.household-name"),
            varName: "name",
            type: fieldTypes.TEXT,
            rules: ["required"],
          },
        ],
        data: {
          groupId: "",
          name: "",
        },
      },
    });

    function openDialog() {
      state.createDialog = true;
      state.createHouseholdForm.data.name = "";
      state.createHouseholdForm.data.groupId = "";
    }

    const router = useRouter();

    function handleRowClick(item: HouseholdInDB) {
      router.push(`/admin/manage/households/${item.id}`);
    }

    async function handleCreateSubmit() {
      if (!refNewHouseholdForm.value?.validate()) {
        return;
      }

      state.createDialog = false;
      await createHousehold(state.createHouseholdForm.data);
    }

    return {
        ...toRefs(state),
        refNewHouseholdForm,
        groups,
        households,
        validators,
        refreshAllHouseholds,
        deleteHousehold,
        handleCreateSubmit,
        openDialog,
        handleRowClick,
    };
  },
  head() {
    return {
      title: this.$t("household.manage-households") as string,
    };
  },
});
</script>
