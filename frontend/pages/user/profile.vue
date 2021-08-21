<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" sm="12" md="12" lg="6">
        <UserProfileCard :user="user" class="mt-14" @refresh="$auth.fetchUser()" />
      </v-col>
      <v-col cols="12" sm="12" md="12" lg="6">
        <UserAPITokenCard :tokens="user.tokens" class="mt-14" @refresh="$auth.fetchUser()" />
      </v-col>
    </v-row>
  </v-container>
</template>
    
<script lang="ts">
import { computed, defineComponent, useContext } from "@nuxtjs/composition-api";
import UserProfileCard from "~/components/Domain/User/UserProfileCard.vue";
import UserAPITokenCard from "~/components/Domain/User/UserAPITokenCard.vue";

export default defineComponent({
  components: { UserProfileCard, UserAPITokenCard },
  layout: "admin",
  setup() {
    const user = computed(() => {
      return useContext().$auth.user;
    });

    return { user };
  },
});
</script>
    
