// TODO Remove this file when upgrading to Vuetify 3.0

export type VTooltip = Vue & {
  deactivate(): void;
}

export type VForm = Vue & {
  validate: () => boolean;
  resetValidation: () => boolean;
  reset: () => void;
};
