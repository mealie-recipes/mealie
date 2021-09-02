<template>
  <v-container fluid>
    <section>
      <BaseCardSectionTitle title="Group Settings">
        Lorem, ipsum dolor sit amet consectetur adipisicing elit. Alias error provident, eveniet, laboriosam assumenda
        earum amet quaerat vel consequatur molestias sed enim. Adipisci a consequuntur dolor culpa expedita voluptatem
        praesentium optio iste atque, ea reiciendis iure non aut suscipit modi ducimus ratione, quam numquam quaerat
        distinctio illum nemo. Dicta, doloremque!
      </BaseCardSectionTitle>
      <div v-if="categories" class="d-flex">
        <DomainRecipeCategoryTagSelector v-model="categories" class="mt-5 mr-5" />
        <BaseButton save class="mt-auto mb-3" @click="actions.updateAll()" />
      </div>
    </section>
  </v-container>
</template>
    
<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";
import { useGroup } from "~/composables/use-groups";

export default defineComponent({
  layout: "admin",
  setup() {
    const { categories, actions } = useGroup();

    return {
      categories,
      actions,
    };
  },
});
</script>
    
<style scoped>
</style>