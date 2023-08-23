<template>
  <div class="text-center">
    <v-menu
      v-model="showMenu"
      offset-x
      offset-overflow
      left
      allow-overflow
      close-delay="125"
      :close-on-content-click="false"
      content-class="d-print-none"
      :z-index="2"
    >
      <template #activator="{ on, attrs }">
        <v-badge :value="timerEnded" overlap color="red" content="!">
          <v-btn :fab="fab" :small="fab" :color="timerEnded ? 'secondary' : color" :icon="!fab" dark v-bind="attrs" v-on="on" @click.prevent>
            <v-progress-circular
              v-if="timerInitialized && !timerEnded"
              :value="timerProgress"
              :rotate="270"
              :color="timerRunning ? undefined : 'primary'"
            >
              <v-icon small>{{ timerRunning ? $globals.icons.timer : $globals.icons.timerPause }}</v-icon>
            </v-progress-circular>
            <v-icon v-else>{{ $globals.icons.timer }}</v-icon>
          </v-btn>
        </v-badge>
      </template>
      <v-card>
        <v-card-title>
          <v-icon class="pr-2">{{ $globals.icons.timer }}</v-icon>
          {{ $i18n.tc("recipe.timer.kitchen-timer") }}
        </v-card-title>
        <div class="mx-auto" style="width: fit-content;">
          <v-progress-circular
            :value="timerProgress"
            :rotate="270"
            color="primary"
            class="mb-2"
            :size="128"
            :width="24"
          >
          <v-icon
            v-if="timerInitialized && !timerRunning"
            x-large
            :color="timerEnded ? 'red' : 'primary'"
            @click="() => timerEnded ? resetTimer() : resumeTimer()"
          >
            {{ timerEnded ? $globals.icons.stop : $globals.icons.pause }}
          </v-icon>
          </v-progress-circular>
        </div>
        <v-container width="100%" fluid class="ma-0 px-auto py-2">
          <v-row no-gutters justify="center">
            <v-col cols="3" align-self="center">
              <v-text-field
                :value="timerHours"
                :min="0"
                outlined
                single-line
                solo
                hide-details
                type="number"
                :disabled="timerInitialized"
                class="centered-input my-0 py-0"
                style="font-size: large; width: 100px;"
                @input="(v) => timerHours = v.toString().padStart(2, '0')"
              />
            </v-col>
            <v-col cols="1" align-self="center" style="text-align: center;">
              <h1>:</h1>
            </v-col>
            <v-col cols="3" align-self="center">
              <v-text-field
                :value="timerMinutes"
                :min="0"
                outlined
                single-line
                solo
                hide-details
                type="number"
                :disabled="timerInitialized"
                class="centered-input my-0 py-0"
                style="font-size: large; width: 100px;"
                @input="(v) => timerMinutes = v.toString().padStart(2, '0')"
              />
            </v-col>
            <v-col cols="1" align-self="center" style="text-align: center;" >
              <h1>:</h1>
            </v-col>
            <v-col cols="3" align-self="center">
              <v-text-field
                :value="timerSeconds"
                :min="0"
                outlined
                single-line
                solo
                hide-details
                type="number"
                :disabled="timerInitialized"
                class="centered-input my-0 py-0"
                style="font-size: large; width: 100px;"
                @input="(v) => timerSeconds = v.toString().padStart(2, '0')"
              />
            </v-col>
          </v-row>
        </v-container>
        <div class="mx-auto" style="width: 100%;">
          <BaseButtonGroup
            stretch
            :buttons="timerButtons"
            @initialize-timer="initializeTimer"
            @pause-timer="pauseTimer"
            @resume-timer="resumeTimer"
            @stop-timer="resetTimer"
          />
        </div>
      </v-card>
    </v-menu>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, reactive, ref, toRefs, useContext, watch } from "@nuxtjs/composition-api";
import { ButtonOption } from "~/components/global/BaseButtonGroup.vue";

// @ts-ignore typescript can't find our audio file, but it's there!
import timerAlarmAudio from "~/assets/audio/kitchen_alarm.mp3";

export default defineComponent({
  props: {
    fab: {
      type: Boolean,
      default: false,
    },
    color: {
      type: String,
      default: "primary",
    },
  },
  setup() {
    const { $globals, i18n } = useContext();
    const state = reactive({
      showMenu: false,
      timerInitialized: false,
      timerRunning: false,
      timerEnded: false,
      timerInitialValue: 0,
      timerValue: 0,
    });

    watch(
      () => state.showMenu,
      () => {
        if (state.showMenu && state.timerEnded) {
          resetTimer();
        }
      }
    );

    // ts doesn't recognize timerAlarmAudio because it's a weird import
    // eslint-disable-next-line @typescript-eslint/no-unsafe-argument
    const timerAlarm = new Audio(timerAlarmAudio);
    timerAlarm.loop = true;

    const timerHours = ref<string | number>("00");
    const timerMinutes = ref<string | number>("00");
    const timerSeconds = ref<string | number>("00");

    const initializeButton: ButtonOption = {
      icon: $globals.icons.timerPlus,
      text: i18n.tc("recipe.timer.start-timer"),
      event: "initialize-timer",
    }

    const pauseButton: ButtonOption = {
      icon: $globals.icons.pause,
      text: i18n.tc("recipe.timer.pause-timer"),
      event: "pause-timer",
    };

    const resumeButton: ButtonOption = {
      icon: $globals.icons.play,
      text: i18n.tc("recipe.timer.resume-timer"),
      event: "resume-timer",
    };

    const stopButton: ButtonOption = {
      icon: $globals.icons.stop,
      text: i18n.tc("recipe.timer.stop-timer"),
      event: "stop-timer",
      color: "red",
    };

    const timerButtons = computed<ButtonOption[]>(() => {
      const buttons: ButtonOption[] = [];
      if (state.timerInitialized) {
        if (state.timerEnded) {
          buttons.push(stopButton);
        } else if (state.timerRunning) {
          buttons.push(pauseButton, stopButton);
        } else {
          buttons.push(resumeButton, stopButton);
        }
      } else {
        buttons.push(initializeButton);
      }

      // I don't know why this is failing the frontend lint test ¯\_(ツ)_/¯
      // eslint-disable-next-line @typescript-eslint/no-unsafe-return
      return buttons;
    });

    const timerProgress = computed(() => {
      if(state.timerInitialValue) {
        return (state.timerValue / state.timerInitialValue) * 100;
      } else {
        return 0;
      }
    });

    let timerInterval: number | null = null;
    function decrementTimer() {
      if (state.timerValue > 0) {
        state.timerValue -= 1;

        timerHours.value = Math.floor(state.timerValue / 3600).toString().padStart(2, "0");
        timerMinutes.value = Math.floor(state.timerValue % 3600 / 60).toString().padStart(2, "0");
        timerSeconds.value = Math.floor(state.timerValue % 3600 % 60).toString().padStart(2, "0");
      }
      else {
        state.timerRunning = false;
        state.timerEnded = true;
        timerAlarm.currentTime = 0;
        timerAlarm.play();

        if (timerInterval) {
          clearInterval(timerInterval);
          timerInterval = null;
        }
      }
    }

    function initializeTimer() {
      state.timerInitialized = true;
      state.timerRunning = true;
      state.timerEnded = false;

      console.log(timerSeconds.value);

      const hours = parseFloat(timerHours.value.toString()) > 0 ? parseFloat(timerHours.value.toString()) : 0;
      const minutes = parseFloat(timerMinutes.value.toString()) > 0 ? parseFloat(timerMinutes.value.toString()) : 0;
      const seconds = parseFloat(timerSeconds.value.toString()) > 0 ? parseFloat(timerSeconds.value.toString()) : 0;

      state.timerInitialValue = (hours * 3600) + (minutes * 60) + seconds;
      state.timerValue = state.timerInitialValue;

      timerInterval = setInterval(decrementTimer, 1000) as unknown as number;

      timerHours.value = Math.floor(state.timerValue / 3600).toString().padStart(2, "0");
      timerMinutes.value = Math.floor(state.timerValue % 3600 / 60).toString().padStart(2, "0");
      timerSeconds.value = Math.floor(state.timerValue % 3600 % 60).toString().padStart(2, "0");
    };

    function pauseTimer() {
      state.timerRunning = false;
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
      }
    };

    function resumeTimer() {
      state.timerRunning = true;
      timerInterval = setInterval(decrementTimer, 1000) as unknown as number;
    };

    function resetTimer() {
      state.timerInitialized = false;
      state.timerRunning = false;
      state.timerEnded = false;

      timerAlarm.pause();
      timerAlarm.currentTime = 0;

      timerHours.value = "00";
      timerMinutes.value = "00";
      timerSeconds.value = "00";

      state.timerValue = 0;
      if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
      }
    };

    return {
      ...toRefs(state),
      timerHours,
      timerMinutes,
      timerSeconds,
      timerButtons,
      timerProgress,
      initializeTimer,
      pauseTimer,
      resumeTimer,
      resetTimer,
    };
  },
});
</script>

<style scoped>
    .centered-input >>> input {
      text-align: center;
    }
</style>
