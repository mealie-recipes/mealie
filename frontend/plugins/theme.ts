export default ({ $vuetify, $config }: any) => {
  $vuetify.theme.themes = $config.themes;

  if ($config.useDark) {
    $vuetify.theme.dark = true;
  }
};
