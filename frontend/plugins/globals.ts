import { icons } from "~/utils/icons";

// eslint-disable-next-line no-empty-pattern
export default ({}, inject: any) => {
  // Inject $hello(msg) in Vue, context and store.
  inject("globals", { icons });
};
