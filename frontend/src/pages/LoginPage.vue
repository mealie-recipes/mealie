<template>
  <v-container fill-height class="text-center">
    <v-row>
      <v-flex class="d-flex justify-center" width="500px">
        <LoginForm @logged-in="redirectMe" class="ma-1" />
      </v-flex>
    </v-row>
    <v-row></v-row>
  </v-container>
</template>

<script>
import LoginForm from "../components/Login/LoginForm";
export default {
  components: {
    LoginForm,
  },
  computed: {
    viewScale() {
      switch (this.$vuetify.breakpoint.name) {
        case "xs":
          return true;
        case "sm":
          return true;
        default:
          return false;
      }
    },
  },
  methods: {
    redirectMe() {
      if (this.$route.query.redirect) {
        this.$router.push(this.$route.query.redirect);
      } else this.$router.push({ path: "/" });
    },
  },
};
</script>

<style>
</style>