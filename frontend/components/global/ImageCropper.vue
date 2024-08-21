<template>
    <v-container class="pa-0">
        <v-row no-gutters>
            <v-col cols="8" align-self="center">
                <Cropper
                    ref="cropper"
                    class="cropper"
                    :src="img"
                    :default-size="defaultSize"
                    :style="`height: ${cropperHeight}; width: ${cropperWidth};`"
                />
            </v-col>
            <v-spacer />
            <v-col cols="2" align-self="center">
                <v-container class="pa-0 mx-0">
                    <v-row v-for="(row, keyRow) in controls" :key="keyRow">
                        <v-col
                            v-for="(control, keyControl) in row" :key="keyControl"
                            :cols="12 / row.length"
                            class="py-2 mx-0"
                            style="display: flex; align-items: center; justify-content: center;"
                        >
                            <v-btn icon :color="control.color" @click="control.callback()">
                                <v-icon> {{ control.icon }} </v-icon>
                            </v-btn>
                        </v-col>
                    </v-row>
                </v-container>
            </v-col>
        </v-row>
    </v-container>
</template>

<script lang="ts">
import { defineComponent, ref, useContext } from "@nuxtjs/composition-api";

import { Cropper } from "vue-advanced-cropper";
import "vue-advanced-cropper/dist/style.css";

export default defineComponent({
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
        }
    },
    setup(_, context) {
        const cropper = ref<Cropper>();
        const { $globals } = useContext();

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
            })
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
        // @ts-expect-error https://advanced-cropper.github.io/vue-advanced-cropper/guides/advanced-recipes.html
        defaultSize({ imageSize, visibleArea }) {
            return {
                width: (visibleArea || imageSize).width,
                height: (visibleArea || imageSize).height,
            };
        },
    },
});
</script>
