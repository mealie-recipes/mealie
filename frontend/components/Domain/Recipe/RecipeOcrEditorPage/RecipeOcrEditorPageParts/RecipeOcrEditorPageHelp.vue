<template>
  <v-card>
    <v-app-bar dense dark color="primary" class="mb-2">
      <v-icon large left>
        {{ $globals.icons.help }}
      </v-icon>
      <v-toolbar-title class="headline"> Help </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-card-text>
      <h1>Mouse modes</h1>
      <v-divider class="mb-2 mt-1" />
      <h2 class="my-2">
        <v-icon> {{ $globals.icons.selectMode }} </v-icon>{{ $t("ocr-editor.help.selection-mode") }}
      </h2>
      <p class="my-1">{{ $t("ocr-editor.help.selection-mode") }}</p>
      <ol>
        <li>{{ $t("ocr-editor.help.selection-mode-steps.draw") }}</li>
        <li>{{ $t("ocr-editor.help.selection-mode-steps.click") }}</li>
        <li>{{ $t("ocr-editor.help.selection-mode-steps.result") }}</li>
      </ol>
      <h2 class="my-2">
        <v-icon> {{ $globals.icons.panAndZoom }} </v-icon>{{ $t("ocr-editor.help.pan-and-zoom-mode") }}
      </h2>
      {{ $t("ocr-editor.help.pan-and-zoom-desc") }}
      <h1 class="mt-5">{{ $t("ocr-editor.help.split-text-mode") }}</h1>
      <v-divider class="mb-2 mt-1" />
      <h2 class="my-2">
        <v-icon> {{ $globals.icons.preserveLines }} </v-icon>
        {{ $t("ocr-editor.help.split-modes.line-mode") }}
      </h2>
      <p>
        {{ $t("ocr-editor.help.split-modes.line-mode-desc") }}
      </p>
      <h2 class="my-2">
        <v-icon> {{ $globals.icons.preserveBlocks }} </v-icon>
        {{ $t("ocr-editor.help.split-modes.block-mode") }}
      </h2>
      <p>
        {{ $t("ocr-editor.help.split-modes.block-mode-desc") }}
      </p>
      <h2 class="my-2">
        <v-icon> {{ $globals.icons.flatten }} </v-icon> {{ $t("ocr-editor.help.split-modes.flat-mode") }}
      </h2>
      <p>{{ $t("ocr-editor.help.split-modes.flat-mode-desc") }}</p>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { defineComponent } from "@nuxtjs/composition-api";

export default defineComponent({});
</script>
