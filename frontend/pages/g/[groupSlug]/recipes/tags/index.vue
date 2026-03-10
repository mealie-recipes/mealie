<template>
  <v-container>
    <!-- Create Tag Group Dialog -->
    <BaseDialog
      v-model="dialogs.createGroup"
      :title="$t('tag.create-a-tag-group')"
      can-confirm
      @confirm="createGroup"
    >
      <v-card-text>
        <v-text-field
          v-model="groupForm.name"
          :label="$t('tag.tag-group-name')"
          autofocus
        />
        <InputColor v-model="groupForm.color" />
        <v-text-field
          v-model.number="groupForm.position"
          :label="$t('tag.tag-group-position')"
          type="number"
          min="0"
        />
      </v-card-text>
    </BaseDialog>

    <!-- Update Tag Group Dialog -->
    <BaseDialog
      v-if="updateGroupTarget"
      v-model="dialogs.updateGroup"
      :title="$t('general.update')"
      can-confirm
      @confirm="updateGroup"
    >
      <v-card-text>
        <v-text-field
          v-model="updateGroupTarget.name"
          :label="$t('tag.tag-group-name')"
          autofocus
        />
        <InputColor v-model="updateGroupTarget.color" />
        <v-text-field
          v-model.number="updateGroupTarget.position"
          :label="$t('tag.tag-group-position')"
          type="number"
          min="0"
        />
      </v-card-text>
    </BaseDialog>

    <!-- Delete Tag Group Dialog -->
    <BaseDialog
      v-if="deleteGroupTarget"
      v-model="dialogs.deleteGroup"
      :title="$t('general.delete-with-name', { name: $t('tag.tag-group') })"
      color="error"
      :icon="$globals.icons.alertCircle"
      can-confirm
      @confirm="deleteGroup"
    >
      <v-card-text>
        <p>{{ $t('general.confirm-delete-generic-with-name', { name: $t('tag.tag-group') }) }}</p>
        <p class="mt-4 mb-0 ml-4">{{ deleteGroupTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Create Tag Dialog -->
    <BaseDialog
      v-model="dialogs.createTag"
      :title="$t('tag.create-a-tag')"
      can-confirm
      @confirm="createTag"
    >
      <v-card-text>
        <v-text-field
          v-model="tagForm.name"
          :label="$t('tag.tag-name')"
          autofocus
        />
        <v-select
          v-model="tagForm.tagGroupId"
          :items="tagGroupStore"
          :label="$t('tag.tag-group')"
          item-title="name"
          item-value="id"
          clearable
        />
      </v-card-text>
    </BaseDialog>

    <!-- Update Tag Dialog -->
    <BaseDialog
      v-if="updateTagTarget"
      v-model="dialogs.updateTag"
      :title="$t('general.update')"
      can-confirm
      @confirm="updateTag"
    >
      <v-card-text>
        <v-text-field
          v-model="updateTagTarget.name"
          :label="$t('tag.tag-name')"
          autofocus
        />
        <v-select
          v-model="updateTagTarget.tagGroupId"
          :items="tagGroupStore"
          :label="$t('tag.tag-group')"
          item-title="name"
          item-value="id"
          clearable
        />
      </v-card-text>
    </BaseDialog>

    <!-- Delete Tag Dialog -->
    <BaseDialog
      v-if="deleteTagTarget"
      v-model="dialogs.deleteTag"
      :title="$t('general.delete-with-name', { name: $t('tag.tag') })"
      color="error"
      :icon="$globals.icons.alertCircle"
      can-confirm
      @confirm="deleteTag"
    >
      <v-card-text>
        <p>{{ $t('general.confirm-delete-generic-with-name', { name: $t('tag.tag') }) }}</p>
        <p class="mt-4 mb-0 ml-4">{{ deleteTagTarget.name }}</p>
      </v-card-text>
    </BaseDialog>

    <!-- Search -->
    <v-row dense>
      <v-col>
        <v-text-field
          v-model="searchString"
          variant="outlined"
          autofocus
          color="primary accent-3"
          :placeholder="$t('search.search-placeholder')"
          :prepend-inner-icon="$globals.icons.search"
          clearable
        />
      </v-col>
    </v-row>

    <!-- Toolbar with two create buttons -->
    <v-app-bar
      color="transparent"
      flat
      class="mt-n1 rounded align-center position-relative w-100 left-0 top-0"
    >
      <v-icon size="large" start>
        {{ $globals.icons.tags }}
      </v-icon>
      <v-toolbar-title class="headline">
        {{ $t("tag.tags") }}
      </v-toolbar-title>
      <v-spacer />
      <BaseButton
        create
        secondary
        :text="$t('tag.tag-group')"
        class="mr-2"
        @click="openCreateGroupDialog"
      />
      <BaseButton
        create
        :text="$t('tag.tag')"
        @click="dialogs.createTag = true"
      />
    </v-app-bar>

    <!-- Tag group sections (replace letter sections) -->
    <template v-for="group in visibleGroups" :key="group.id">
      <section class="my-4">
        <!-- Section header: group name with color accent + context menu -->
        <div class="d-flex align-center">
          <div
            class="text-h5 flex-grow-1 py-1"
            :style="group.color ? { borderLeft: `4px solid ${group.color}`, paddingLeft: '10px' } : { paddingLeft: '2px' }"
            style="font-weight: normal;"
          >
            {{ group.name }}
          </div>
          <ContextMenu
            :items="[groupPresets.edit, groupPresets.delete]"
            @edit="openUpdateGroupDialog(group)"
            @delete="openDeleteGroupDialog(group)"
          />
        </div>
        <v-divider class="mt-1 mb-3" />
        <v-row>
          <v-col
            v-for="tag in tagsByGroup[group.id]"
            :key="tag.id"
            cols="12"
            sm="12"
            md="6"
            lg="4"
            xl="3"
          >
            <v-card
              :class="!group.color ? 'left-border' : ''"
              :style="group.color ? { borderLeft: `5px solid ${group.color}` } : {}"
              hover
              :to="`/g/${groupSlug}?tags=${tag.id}`"
            >
              <v-card-actions>
                <v-icon>{{ $globals.icons.tags }}</v-icon>
                <v-card-title class="py-1 text-truncate flex-shrink-1 flex-grow-1">
                  {{ tag.name }}
                </v-card-title>
                <ContextMenu
                  :items="[presets.delete, presets.edit]"
                  @delete="openDeleteTagDialog(tag)"
                  @edit="openUpdateTagDialog(tag)"
                />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </section>
    </template>

    <!-- Ungrouped tags section -->
    <section v-if="ungroupedTags.length > 0" class="my-4">
      <div class="d-flex align-center">
        <div class="text-h5 flex-grow-1 py-1" style="font-weight: normal; padding-left: 2px;">
          {{ $t('tag.ungrouped') }}
        </div>
      </div>
      <v-divider class="mt-1 mb-3" />
      <v-row>
        <v-col
          v-for="tag in ungroupedTags"
          :key="tag.id"
          cols="12"
          sm="12"
          md="6"
          lg="4"
          xl="3"
        >
          <v-card
            class="left-border"
            hover
            :to="`/g/${groupSlug}?tags=${tag.id}`"
          >
            <v-card-actions>
              <v-icon>{{ $globals.icons.tags }}</v-icon>
              <v-card-title class="py-1 text-truncate flex-shrink-1 flex-grow-1">
                {{ tag.name }}
              </v-card-title>
              <ContextMenu
                :items="[presets.delete, presets.edit]"
                @delete="openDeleteTagDialog(tag)"
                @edit="openUpdateTagDialog(tag)"
              />
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </section>

    <!-- Empty state -->
    <div v-if="visibleGroups.length === 0 && ungroupedTags.length === 0" class="text-center mt-8 text-medium-emphasis">
      {{ $t('search.no-results') }}
    </div>
  </v-container>
</template>

<script setup lang="ts">
import Fuse from "fuse.js";
import { useTagStore, useTagGroupStore } from "~/composables/store";
import { useContextPresets } from "~/composables/use-context-presents";
import { deepCopy } from "~/composables/use-utils";
import { useRouteQuery } from "~/composables/use-router";
import type { TagOut, TagGroupOut } from "~/lib/api/types/recipe";

definePageMeta({ middleware: ["group-only"] });

const i18n = useI18n();
const auth = useMealieAuth();
const route = useRoute();
const groupSlug = computed(() => route.params.groupSlug as string || auth.user.value?.groupSlug || "");

useSeoMeta({ title: i18n.t("tag.tags") });

const { store: tagStore, actions: tagActions } = useTagStore();
const { store: tagGroupStore, actions: tagGroupActions } = useTagGroupStore();
const presets = useContextPresets();

// Context menu preset for groups (edit only, no delete confirmation shortcut)
const groupPresets = {
  edit: presets.edit,
  delete: presets.delete,
};

// ============================================================
// Search

const searchString = useRouteQuery("q", "");

const fuseOptions = {
  ignoreLocation: true,
  shouldSort: true,
  threshold: 0.2,
  keys: ["name"],
};

const fuse = computed(() => new Fuse(tagStore.value as TagOut[], fuseOptions));

const filteredTags = computed<TagOut[]>(() => {
  if (!searchString.value.trim()) return tagStore.value as TagOut[];
  return fuse.value.search(searchString.value.trim()).map(r => r.item);
});

// ============================================================
// Grouping

const tagsByGroup = computed(() => {
  const result: Record<string, TagOut[]> = {};
  for (const tag of filteredTags.value) {
    const gid = (tag as any).tagGroupId;
    if (gid) {
      if (!result[gid]) result[gid] = [];
      result[gid].push(tag);
    }
  }
  // Sort tags within each group alphabetically
  for (const gid of Object.keys(result)) {
    result[gid].sort((a, b) => a.name.localeCompare(b.name));
  }
  return result;
});

const ungroupedTags = computed<TagOut[]>(() =>
  filteredTags.value
    .filter(t => !(t as any).tagGroupId)
    .sort((a, b) => a.name.localeCompare(b.name)),
);

// Only show groups that have tags visible after search
const visibleGroups = computed(() =>
  [...tagGroupStore.value]
    .filter(g => (tagsByGroup.value[g.id] ?? []).length > 0)
    .sort((a, b) => a.position - b.position || a.name.localeCompare(b.name)),
);

// ============================================================
// Dialogs state

const dialogs = ref({
  createGroup: false,
  updateGroup: false,
  deleteGroup: false,
  createTag: false,
  updateTag: false,
  deleteTag: false,
});

// ============================================================
// Tag Group CRUD

const defaultGroupForm = () => ({ name: "", color: "", position: 0 });
const groupForm = ref(defaultGroupForm());
const updateGroupTarget = ref<TagGroupOut | null>(null);
const deleteGroupTarget = ref<TagGroupOut | null>(null);

function openCreateGroupDialog() {
  groupForm.value = defaultGroupForm();
  dialogs.value.createGroup = true;
}

async function createGroup() {
  if (!groupForm.value.name) return;
  await tagGroupActions.createOne({
    name: groupForm.value.name,
    color: groupForm.value.color || null,
    position: groupForm.value.position,
  });
  dialogs.value.createGroup = false;
}

function openUpdateGroupDialog(group: TagGroupOut) {
  updateGroupTarget.value = { ...deepCopy(group), color: group.color ?? "" };
  dialogs.value.updateGroup = true;
}

async function updateGroup() {
  if (!updateGroupTarget.value) return;
  await tagGroupActions.updateOne({
    ...updateGroupTarget.value,
    color: updateGroupTarget.value.color || null,
  });
  dialogs.value.updateGroup = false;
  updateGroupTarget.value = null;
}

function openDeleteGroupDialog(group: TagGroupOut) {
  deleteGroupTarget.value = group;
  dialogs.value.deleteGroup = true;
}

async function deleteGroup() {
  if (!deleteGroupTarget.value) return;
  await tagGroupActions.deleteOne(deleteGroupTarget.value.id);
  dialogs.value.deleteGroup = false;
  deleteGroupTarget.value = null;
}

// ============================================================
// Tag CRUD

const defaultTagForm = () => ({ name: "", tagGroupId: null as string | null });
const tagForm = ref(defaultTagForm());
const updateTagTarget = ref<(TagOut & { tagGroupId?: string | null }) | null>(null);
const deleteTagTarget = ref<TagOut | null>(null);

async function createTag() {
  if (!tagForm.value.name) return;
  await tagActions.createOne({ name: tagForm.value.name, tagGroupId: tagForm.value.tagGroupId } as any);
  dialogs.value.createTag = false;
  tagForm.value = defaultTagForm();
}

function openUpdateTagDialog(tag: TagOut) {
  updateTagTarget.value = deepCopy(tag) as TagOut & { tagGroupId?: string | null };
  dialogs.value.updateTag = true;
}

async function updateTag() {
  if (!updateTagTarget.value) return;
  await tagActions.updateOne(updateTagTarget.value as any);
  dialogs.value.updateTag = false;
  updateTagTarget.value = null;
}

function openDeleteTagDialog(tag: TagOut) {
  deleteTagTarget.value = tag;
  dialogs.value.deleteTag = true;
}

async function deleteTag() {
  if (!deleteTagTarget.value) return;
  await tagActions.deleteOne(deleteTagTarget.value.id);
  dialogs.value.deleteTag = false;
  deleteTagTarget.value = null;
}
</script>
