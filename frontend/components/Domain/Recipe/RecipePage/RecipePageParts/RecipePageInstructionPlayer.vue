<template>
    <span class="v-btn__content">
        <i v-if="!playing.value" aria-hidden="true" class="v-icon notranslate mdi mdi-play theme--dark" @click.stop="play"></i>
        <i v-if="playing.value" aria-hidden="true" class="v-icon notranslate mdi mdi-pause theme--dark" @click.stop="pause"></i>
    </span>
</template>

<script lang="ts">
import { defineComponent, onUnmounted } from "@nuxtjs/composition-api";
import { RecipeStep } from "~/lib/api/types/recipe";
import { NoUndefinedField } from "~/lib/api/types/non-generated";

export default defineComponent({
  props: {
    step: {
      type: Object as () => NoUndefinedField<RecipeStep>,
      required: true
    }
  },
  setup() {
    onUnmounted(() => {
        speechSynthesis.stop();
    });
  },
  data() {
    return {
        playing: false,
        played: false,
        utterance: null,
        currentIndex: {
            type: Number,
            default: 0
        }
    }
  },
  methods: {
    play() {
        const self = this;
        if (this.utterance && this.playing) {
            speechSynthesis.cancel();
        }

        this.utterance = new SpeechSynthesisUtterance(this.step.text);
        this.utterance.onstart = (event) => {
            self.playing = true;
            // self.$emit("playing", true); // TODO: Consider if this event should bubble or a proxy of it should.

            console.debug("Now playing: " + this.step.text);
        };
        this.utterance.onend = () => {
            self.playing = false;
            // self.$emit("playing", false);

            console.debug("Playback complete");
        };

        this.utterance.onpause = () => {
            self.playing = false;
        };

        this.utterance.onresume = () => {
            self.playing = true;
        };

        this.utterance.onboundary = (event) => {
            // Update the start of the current sentence.
            if (event.name === "sentence") {
                self.currentIndex = event.charIndex;
            }
        };
        // TODO: Evaluate the usefulness of this event.
        // this.utterance.onmark = (event) => {
        //     console.log("mark")
        //     console.log(event)
        // };
        this.utterance.onerror = (event) => {
            console.error("Error in playback")
            console.debug(event)
        };

        speechSynthesis.speak(this.utterance);
        return true;
    },
    pause() {
        console.log("Stop playing");
        speechSynthesis.pause();
    }
  }
});
</script>

<style lang="css" scoped>
</style>
