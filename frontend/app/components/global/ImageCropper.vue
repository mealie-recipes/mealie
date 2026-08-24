<template>
  <v-card class="ma-0 pt-2" :elevation="4">
    <v-card-text>
      <!-- Controls Row (Menu) -->
      <v-row class="mb-2 mx-1">
        <v-btn
          color="error"
          :icon="$globals.icons.delete"
          :disabled="submitted"
          @click="$emit('delete')"
        />
        <v-spacer />
        <v-btn
          v-if="changed"
          class="mr-2"
          color="success"
          :icon="$globals.icons.save"
          :disabled="submitted"
          @click="save"
        />
        <v-menu offset-y :close-on-content-click="false" location="bottom center">
          <template #activator="{ props: slotProps }">
            <v-btn color="info" v-bind="slotProps" :icon="$globals.icons.edit" :disabled="submitted" />
          </template>
          <v-list class="mt-1">
            <template v-for="(row, keyRow) in controls" :key="keyRow">
              <v-list-item-group>
                <v-list-item
                  v-for="(control, keyControl) in row"
                  :key="keyControl"
                  :disabled="submitted"
                  @click="control.callback()"
                >
                  <v-list-item-icon>
                    <v-icon :color="control.color" :icon="control.icon" />
                  </v-list-item-icon>
                </v-list-item>
              </v-list-item-group>
            </template>
          </v-list>
        </v-menu>
      </v-row>

      <!-- Image Row -->
      <Cropper
        ref="cropper"
        class="cropper"
        :src="img"
        :default-size="defaultSize"
        :style="`width: ${cropperWidth}; aspect-ratio: ${aspectRatio};`"
        @change="changed = changed + 1"
        @ready="onReady"
      />
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { Cropper } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";

defineProps({
  img: {
    type: String,
    required: true,
  },
  cropperWidth: {
    type: String,
    default: undefined,
  },
  submitted: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits<{
  (e: "save", item: Blob): void;
  (e: "delete"): void;
}>();

const cropper = ref<any>(null);
const changed = ref(0);
// Left to the cropper's own sizing until the image is rotated; see rotate().
const aspectRatio = ref<string | number>("auto");
const { $globals } = useNuxtApp();

function onReady() {
  aspectRatio.value = "auto";
  changed.value = -1;
}

type Control = {
  color: string;
  icon: string;
  callback: CallableFunction;
};

function flip(hortizontal: boolean, vertical?: boolean) {
  if (!cropper.value) return;
  cropper.value.flip(hortizontal, vertical);
  changed.value = changed.value + 1;
}

async function rotate(angle: number) {
  if (!cropper.value) return;
  cropper.value.rotate(angle);
  changed.value = changed.value + 1;

  // A quarter turn swaps the image's width and height. Pin the box to the new
  // orientation, otherwise the cropper keeps the visible area it computed for
  // the old one and part of the rotated image ends up outside of it.
  const { image } = cropper.value.getResult();
  const quarterTurned = Math.abs(image.transforms.rotate % 180) === 90;
  aspectRatio.value = quarterTurned ? image.height / image.width : image.width / image.height;

  // the cropper measures its own box, so let the new size land first
  await nextTick();
  cropper.value.refresh();
}

const controls = ref<Control[][]>([
  [
    {
      color: "info",
      icon: $globals.icons.flipHorizontal,
      callback: () => flip(true, false),
    },
    {
      color: "info",
      icon: $globals.icons.flipVertical,
      callback: () => flip(false, true),
    },
  ],
  [
    {
      color: "info",
      icon: $globals.icons.rotateLeft,
      callback: () => rotate(-90),
    },
    {
      color: "info",
      icon: $globals.icons.rotateRight,
      callback: () => rotate(90),
    },
  ],
]);

function save() {
  if (!cropper.value) return;
  const { canvas } = cropper.value.getResult();
  if (!canvas) return;
  canvas.toBlob((blob) => {
    if (blob) {
      emit("save", blob);
    }
  });
}

function defaultSize({ imageSize, visibleArea }: any) {
  return {
    width: (visibleArea || imageSize).width,
    height: (visibleArea || imageSize).height,
  };
}
</script>
