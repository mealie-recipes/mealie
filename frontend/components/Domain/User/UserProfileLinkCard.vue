<template>
  <v-card
    variant="outlined"
    style="border-color: lightgrey;"
    :to="link.to"
    height="100%"
    class="d-flex flex-column mt-4"
  >
    <div
      v-if="$vuetify.display.smAndDown"
      class="pa-2 mx-auto"
    >
      <v-img
        width="150px"
        height="125"
        :src="image"
      />
    </div>
    <div class="d-flex justify-space-between">
      <div>
        <v-card-title class="text-subtitle-1 pb-0">
          <slot name="title" />
        </v-card-title>
        <div class="d-flex justify-center align-center">
          <v-card-text class="d-flex flex-row mb-auto">
            <slot name="default" />
          </v-card-text>
        </div>
      </div>
      <div
        v-if="$vuetify.display.mdAndUp"
        class="py-2 px-10 my-auto"
      >
        <v-img
          width="150px"
          height="125"
          :src="image"
        />
      </div>
    </div>
    <v-spacer />
    <v-divider />
    <v-card-actions>
      <v-btn
        variant="text"
        color="info"
        :to="link.to"
      >
        {{ link.text }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts" setup>
interface LinkProp {
  text: string;
  url?: string;
  to: string;
}

const props = defineProps({
  link: {
    type: Object as () => LinkProp,
    required: true,
  },
  image: {
    type: String,
    required: false,
    default: "",
  },
});

console.log("Props", props);
</script>
