<template>
    <div v-if="ttsSupported" class="v-btn__content">
        <i v-if="canPlay" aria-hidden="true" class="v-icon notranslate mdi mdi-play theme--dark" @click.stop="play"></i>
        <i v-if="canPause" aria-hidden="true" class="v-icon notranslate mdi mdi-pause theme--dark" @click.stop="pause"></i>
        <i v-if="canResume" aria-hidden="true" class="v-icon notranslate mdi mdi-play theme--dark" @click.stop="resume"></i>
        <i v-if="canStartAgain" aria-hidden="true" class="v-icon notranslate mdi mdi-restart theme--dark" @click.stop="play"></i>

        <small @click.stop="pauseOrResume">{{ currentSentence }}</small>
    </div>
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
        if (speechSynthesis) {
            speechSynthesis.cancel();
        }
    });
  },
  data() {
    return {
        playing: false,
        played: false,
        paused: false,
        utterance: SpeechSynthesisUtterance,
        currentIndex: 0
    }
  },
  computed: {
    ttsSupported() {
        return !!speechSynthesis;
    },
    canPlay() {
        return !this.playing && !this.paused;
    },
    canPause() {
        return this.playing && !this.paused;
    },
    canResume() {
        return !this.playing && this.paused;
    },
    canStartAgain() {
        return this.playing || this.paused;
    },
    nextIndex() {
        // TODO: i18n stopwords in sync with the browser's implementation? Assumes . and ! are boundaries, may not be true for all languages.
        const match = this.step.text.slice(this.currentIndex).search(/[.!]/)
        if (match === -1) {
            return this.currentIndex;
        }
        return this.currentIndex + match;
    },
    currentSentence() {
        if (this.playing || this.paused) {
            return this.step.text.slice(this.currentIndex, this.nextIndex);
        }
        return "";
    }
  },
  methods: {
    pauseOrResume() {
        if (this.paused) {
            this.resume();
        } else {
            this.pause();
        }
    },
    play() {
        speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(this.step.text);
        utterance.onstart = (event) => {
            this.playing = true;
            this.played = false;
            this.paused = false;
            // this.$emit("playing", true); // TODO: Consider if this event should bubble or a proxy of it should.

            console.debug("Now playing: " + this.step.text);
        };
        utterance.onend = () => {
            this.playing = false;
            this.played = true;
            this.paused = false;
            this.$emit("ttscompleted", true);

            console.debug("Playback complete");
        };

        utterance.onpause = () => {
            this.playing = false;
            this.paused = true;
        };

        utterance.onresume = () => {
            this.playing = true;
            this.paused = false;
        };

        utterance.onboundary = (event) => {
            // Update the start of the current sentence.
            if (event.name === "sentence") {
                this.currentIndex = event.charIndex;
            }
        };
        // TODO: Evaluate the usefulness of this event.
        // this.utterance.onmark = (event) => {
        //     console.log("mark")
        //     console.log(event)
        // };
        utterance.onerror = (event) => {
            if (event.error === "interrupted") {
                this.playing = false;
                this.played = false;
                this.paused = false;
            } else {
                console.error("Error in playback")
                console.debug(event);
            }
        };

        speechSynthesis.speak(utterance);

        this.utterance = utterance;
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
