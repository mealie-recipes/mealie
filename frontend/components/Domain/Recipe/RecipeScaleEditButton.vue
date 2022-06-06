<template>
    <div class="text-center">
        <v-menu v-model="menu" offset-y top nudge-top="6" :close-on-content-click="false">
            <template #activator="{ on, attrs }">
                <v-btn color="secondary darken-1" small v-bind="attrs" v-on="on">
                    <span v-if="recipeYield">
                        <span v-if="scale == 1">{{ scaledYield }} {{ $tc('recipe.servings') }}</span>
                        <span v-if="scale != 1"> {{ basicYield }} x {{ scale }} = {{ scaledYield }}
                            {{ $tc('recipe.servings') }}</span>
                    </span>
                    <span v-if="!recipeYield">
                        <span> x {{ scale }}</span>
                    </span>
                </v-btn>
            </template>
            <v-card width="400">
                <v-card-title class="headline flex mb-0">
                    {{ $t("recipe.edit-scale") }}
                </v-card-title>
                <v-card-text class="mt-n5">
                    <div class="mt-4 d-flex align-center">
                        <v-text-field v-model="tempScale" type="number" :min="0" :label="$t('recipe.edit-scale')"
                            @input="emitScale" />
                        <v-tooltip right color="secondary darken-1">
                            <template #activator="{ on, attrs }">
                                <v-btn icon class="mx-1" small v-on="on" @click="tempScale = 1; emitScale()">
                                    <v-icon>
                                        {{ $globals.icons.undo }}
                                    </v-icon>
                                </v-btn>
                            </template>
                            <span> Reset Scale </span>
                        </v-tooltip>
                    </div>
                </v-card-text>
            </v-card>
        </v-menu>
    </div>
</template>

<script lang="ts">
import { defineComponent, reactive, toRefs } from "@nuxtjs/composition-api";

const SCALE_UPDATED_EVENT = "updateScale";

export default defineComponent({
    props: {
        recipeYield: {
            type: String,
            default: null
        },
        basicYield: {
            type: String,
            default: null
        },
        scaledYield: {
            type: String,
            default: null
        },
        scale: {
            type: Number,
            required: true,
        },
    },
    setup(props, context) {
        const state = reactive({
            tempScale: 1,
            menu: false,
        })

        function emitScale() {
            // If text input is empty => type is string and value = ""
            // Therefore for type safety, it is again parsed into a Float or NaN
            // If it is NaN it is directly set to 0 as "" equals 0
            const newScaleNumber = parseFloat(`${state.tempScale}`);
            context.emit(SCALE_UPDATED_EVENT, isNaN(newScaleNumber) ? 0 : newScaleNumber);
        }

        return {
            ...toRefs(state),
            emitScale,
        };
    },
    watch: {
        scale: function (newVal, oldVal) {
            this.tempScale = newVal;
        }
    }
});
</script>

<style lang="scss" scoped>
</style>
