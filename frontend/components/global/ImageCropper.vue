<template>
  <v-card class="ma-0 pt-2" :elevation="4">
    <v-card-text>
      <!-- Controls Row (Menu) -->
      <v-row class="mb-2 mx-1">
        <v-btn
          color="error"
          :icon="$globals.icons.delete"
          @click="$emit('delete')"
        />
        <v-spacer />
        <v-menu offset-y :close-on-content-click="false">
          <template #activator="{ props }">
            <v-btn color="info" v-bind="props" :icon="$globals.icons.edit" />
          </template>
          <v-list>
            <template v-for="(row, keyRow) in controls" :key="keyRow">
              <v-list-item-group>
                <v-list-item
                  v-for="(control, keyControl) in row"
                  :key="keyControl"
                  @click="control.callback()"
                >
                  <v-list-item-icon>
                    <v-icon :color="control.color">
                      {{ control.icon }}
                    </v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <!-- Optionally, you can add a label here if you want -->
                  </v-list-item-content>
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
        :style="`height: ${cropperHeight}; width: ${cropperWidth};`"
      />
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { Cropper } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";

export default defineNuxtComponent({
  components: { Cropper },
  props: {
    img: {
      type: String,
      required: true,
    },
    cropperHeight: {
      type: String,
      default: undefined,
    },
    cropperWidth: {
      type: String,
      default: undefined,
    },
  },
  emits: ["save", "delete"],
  setup(_, context) {
    const cropper = ref<any>();
    const { $globals } = useNuxtApp();

    interface Control {
      color: string;
      icon: string;
      callback: CallableFunction;
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
      [
        {
          color: "success",
          icon: $globals.icons.save,
          callback: () => save(),
        },
      ],
    ]);

    function flip(hortizontal: boolean, vertical?: boolean) {
      if (!cropper.value) {
        return;
      }

      cropper.value.flip(hortizontal, vertical);
    }

    function rotate(angle: number) {
      if (!cropper.value) {
        return;
      }

      cropper.value.rotate(angle);
    }

    function save() {
      if (!cropper.value) {
        return;
      }

      const { canvas } = cropper.value.getResult();
      if (!canvas) {
        return;
      }

      canvas.toBlob((blob) => {
        if (blob) {
          context.emit("save", blob);
        }
      });
    }

    return {
      cropper,
      controls,
      flip,
      rotate,
      save,
    };
  },

  methods: {
    defaultSize({ imageSize, visibleArea }) {
      return {
        width: (visibleArea || imageSize).width,
        height: (visibleArea || imageSize).height,
      };
    },
  },
});
</script>
