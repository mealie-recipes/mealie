<template>
  <v-container fluid>
    <UserProfileCard :user="user" class="mt-14" @refresh="$auth.fetchUser()" />
  </v-container>
</template>
    
<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import UserProfileCard from "~/components/Domain/User/UserProfileCard.vue";

export default defineComponent({
  components: { UserProfileCard },
  setup() {
    const user = computed(() => {
      return useContext().$auth.user;
    });

    return { user };
  },
});
</script>
    
