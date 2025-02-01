<template>
    <span class="v-btn__content">
        <i v-if="!playing" aria-hidden="true" class="v-icon notranslate mdi mdi-play theme--dark" @click.stop="play"></i>
        <i v-if="playing" aria-hidden="true" class="v-icon notranslate mdi mdi-pause theme--dark" @click.stop="pause"></i>
        <i v-if="playing" aria-hidden="true" class="v-icon notranslate mdi mdi-pause theme--dark" @click.stop="resume"></i>
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
        paused: false,
        utterance: null,
        currentIndex: 0
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
            self.played = false;
            self.paused = false;
            // self.$emit("playing", true); // TODO: Consider if this event should bubble or a proxy of it should.

            console.debug("Now playing: " + this.step.text);
        };
        this.utterance.onend = () => {
            self.playing = false;
            self.played = true;
            self.paused = false;
            // self.$emit("playing", false);

            console.debug("Playback complete");
        };

        this.utterance.onpause = () => {
            self.playing = false;
            self.paused = true;
        };

        this.utterance.onresume = () => {
            self.playing = true;
            self.paused = false;
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
        speechSynthesis.pause();
    },
    resume() {
        speechSynthesis.resume();
    }
  }
});
</script>

<style lang="css" scoped>
</style>
