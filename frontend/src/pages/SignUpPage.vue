<template>
  <v-container fill-height class="text-center">
    <v-row>
      <v-flex class="d-flex justify-center" width="500px">
        <SignUpForm @logged-in="redirectMe" class="ma-1" />
      </v-flex>
    </v-row>
    <v-row></v-row>
  </v-container>
</template>

<script>
import SignUpForm from "../components/Login/SignUpForm";
export default {
  components: {
    SignUpForm,
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