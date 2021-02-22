<template>
  <v-row justify="start" height="100%">
    <v-col align="center">
      <LoginForm />
    </v-col>
  </v-row>
</template>

<script>
import LoginForm from "../components/Login/LoginForm";
export default {
  components: {
    LoginForm,
  },
};
</script>

<style>
</style>