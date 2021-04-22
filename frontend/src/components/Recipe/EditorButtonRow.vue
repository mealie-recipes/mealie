<template>
  <v-expand-transition>
    <v-toolbar
      class="card-btn pt-1"
      flat
      :height="isSticky ? null : '0'"
      :extension-height="isSticky ? '20' : '0'"
      color="rgb(255, 0, 0, 0.0)"
    >
      <ConfirmationDialog
        :title="$t('recipe.delete-recipe')"
        :message="$t('recipe.delete-ConfirmationDialog')"
        color="error"
        icon="mdi-alert-circle"
        ref="deleteRecipieConfirm"
        v-on:confirm="deleteRecipe()"
      />
      <template v-slot:extension>
        <v-col></v-col>
        <div v-if="open">
          <v-btn
            class="mr-2"
            fab
            dark
            small
            color="error"
            @click="deleteRecipeConfrim"
          >
            <v-icon>mdi-delete</v-icon>
          </v-btn>

          <v-btn class="mr-2" fab dark small color="success" @click="save">
            <v-icon>mdi-content-save</v-icon>
          </v-btn>
          <v-btn class="mr-5" fab dark small color="secondary" @click="json">
            <v-icon>mdi-code-braces</v-icon>
          </v-btn>
        </div>
        <v-btn color="accent" fab dark small @click="editor">
          <v-icon>mdi-square-edit-outline</v-icon>
        </v-btn>
      </template>
    </v-toolbar>
  </v-expand-transition>
</template>

<script>
import ConfirmationDialog from "@/components/UI/Dialogs/ConfirmationDialog.vue";

export default {
  props: {
    open: {
      type: Boolean,
      default: true,
    },
  },

  components: {
    ConfirmationDialog,
  },
  data() {
    return {
      stickyTop: 50,
      scrollPosition: null,
    };
  },
  mounted() {
    window.addEventListener("scroll", this.updateScroll);
  },
  destroy() {
    window.removeEventListener("scroll", this.updateScroll);
  },

  computed: {
    isSticky() {
      return this.scrollPosition >= 500;
    },
  },

  methods: {
    editor() {
      this.$emit("editor");
    },
    save() {
      this.$emit("save");
    },
    updateScroll() {
      this.scrollPosition = window.scrollY;
    },

    deleteRecipeConfrim() {
      this.$refs.deleteRecipieConfirm.open();
    },
    deleteRecipe() {
      this.$emit("delete");
    },
    json() {
      this.$emit("json");
    },
  },
};
</script>

<style>
</style>