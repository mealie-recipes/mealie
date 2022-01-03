// Type definition such that $vuetify is available in Nuxt context
// TODO Possibly replace vuetify with @nuxtjs/vuetify
// Then this type definition would happen automatically

import {Framework} from "vuetify";

declare module "@nuxt/types" {
  interface Context {
    $vuetify: Framework;
  }
}
