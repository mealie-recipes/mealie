// vetur.config.js
/** @type {import('vls').VeturConfig} */
module.exports = {
  settings: {
    "vetur.useWorkspaceDependencies": true,
    "vetur.experimental.templateInterpolationService": true,
    "vetur.validation.interpolation": false,
  },
  projects: [
    {
      root: "./frontend",
      package: "package.json",
      globalComponents: ["./src/components/**/*.vue"],
    },
  ],
};
