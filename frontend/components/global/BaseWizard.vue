<template>
  <div :style="`width: ${width}; height: 100%;`">
    <LanguageDialog v-model="langDialog" />
    <v-card>
      <div>
        <v-toolbar width="100%" color="primary" class="d-flex justify-center" style="margin-bottom: 4rem" dark>
          <v-toolbar-title class="headline text-h4"> Mealie </v-toolbar-title>
        </v-toolbar>

        <div class="icon-container">
          <v-divider class="icon-divider"></v-divider>
          <v-avatar class="pa-2 icon-avatar" color="primary" size="75">
            <svg class="icon-white" style="width: 75" viewBox="0 0 24 24">
              <path
                d="M8.1,13.34L3.91,9.16C2.35,7.59 2.35,5.06 3.91,3.5L10.93,10.5L8.1,13.34M13.41,13L20.29,19.88L18.88,21.29L12,14.41L5.12,21.29L3.71,19.88L13.36,10.22L13.16,10C12.38,9.23 12.38,7.97 13.16,7.19L17.5,2.82L18.43,3.74L15.19,7L16.15,7.94L19.39,4.69L20.31,5.61L17.06,8.85L18,9.81L21.26,6.56L22.18,7.5L17.81,11.84C17.03,12.62 15.77,12.62 15,11.84L14.78,11.64L13.41,13Z"
              />
            </svg>
          </v-avatar>
        </div>
      </div>
      <div class="d-flex justify-center grow items-center my-4">
        <slot :width="pageWidth"></slot>
      </div>
      <div class="mx-2 my-4">
        <v-progress-linear
          v-if="value > 0"
          :value="Math.ceil((value/maxPageNumber)*100)"
          striped
          height="10"
        />
      </div>
      <v-divider class="ma-2" />
      <v-card-actions width="100%">
        <v-btn
          v-if="prevButtonShow"
          :disabled="!prevButtonEnable"
          :color="prevButtonColor"
          @click="decrementPage"
        >
          <v-icon v-if="prevButtonIconRef">
            {{ prevButtonIconRef }}
          </v-icon>
          {{ prevButtonTextRef }}
        </v-btn>
        <v-spacer />
        <v-btn
          v-if="nextButtonShow"
          :disabled="!nextButtonEnable"
          :color="nextButtonColorRef"
          @click="incrementPage"
        >
          <div v-if="isSubmitting">
            <v-progress-circular indeterminate color="white" size="24" />
          </div>
          <div v-else>
            <v-icon v-if="nextButtonIconRef && !nextButtonIconAfter">
              {{ nextButtonIconRef }}
            </v-icon>
            {{ nextButtonTextRef }}
            <v-icon v-if="nextButtonIconRef && nextButtonIconAfter">
              {{ nextButtonIconRef }}
            </v-icon>
          </div>
        </v-btn>
      </v-card-actions>
      <v-card-actions class="justify-center flex-column py-8">
        <BaseButton large color="primary" @click="langDialog = true">
          <template #icon> {{ $globals.icons.translate }}</template>
          {{ $t("language-dialog.choose-language") }}
        </BaseButton>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script lang="ts">
import { computed, defineComponent, ref, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
  props: {
    value: {
      type: Number,
      required: true,
    },
    minPageNumber: {
      type: Number,
      default: 0,
    },
    maxPageNumber: {
      type: Number,
      required: true,
    },
    width: {
      type: [String, Number],
      default: "1200px",
    },
    pageWidth: {
      type: [String, Number],
      default: "600px",
    },
    prevButtonText: {
      type: String,
      default: undefined,
    },
    prevButtonIcon: {
      type: String,
      default: null,
    },
    prevButtonColor: {
      type: String,
      default: "grey-darken-3",
    },
    prevButtonShow: {
      type: Boolean,
      default: true,
    },
    prevButtonEnable: {
      type: Boolean,
      default: true,
    },
    nextButtonText: {
      type: String,
      default: undefined,
    },
    nextButtonIcon: {
      type: String,
      default: null,
    },
    nextButtonIconAfter: {
      type: Boolean,
      default: true,
    },
    nextButtonColor: {
      type: String,
      default: undefined,
    },
    nextButtonShow: {
      type: Boolean,
      default: true,
    },
    nextButtonEnable: {
      type: Boolean,
      default: true,
    },
    nextButtonIsSubmit: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      required: true,
    },
    icon: {
      type: String,
      default: null,
    },
    isSubmitting: {
      type: Boolean,
      default: false,
    }
  },
  setup(props, context) {
    const { $globals, i18n } = useContext();
    const ready = ref(false);
    const langDialog = ref(false);

    const prevButtonTextRef = computed(() => props.prevButtonText || i18n.tc("general.back"));
    const prevButtonIconRef = computed(() => props.prevButtonIcon || $globals.icons.back);
    const nextButtonTextRef = computed(
      () => props.nextButtonText || (
          props.nextButtonIsSubmit ? i18n.tc("general.submit") : i18n.tc("general.next")
        )
      );
    const nextButtonIconRef = computed(
      () => props.nextButtonIcon || (
          props.nextButtonIsSubmit ? $globals.icons.createAlt : $globals.icons.forward
      )
    );
    const nextButtonColorRef = computed(
      () => props.nextButtonColor || (props.nextButtonIsSubmit ? "success" : "info")
    );

    function goToPage(page: number) {
      if (page < props.minPageNumber) {
        goToPage(props.minPageNumber);
        return;
      } else if (page > props.maxPageNumber) {
        goToPage(props.maxPageNumber);
        return;
      }

      context.emit("input", page);
    }

    function decrementPage() {
      goToPage(props.value - 1);
    }

    function incrementPage() {
      if (props.nextButtonIsSubmit) {
        context.emit("submit", props.value);
      } else {
        goToPage(props.value + 1);
      }
    }

    ready.value = true;

    return {
      ready,
      langDialog,
      prevButtonTextRef,
      prevButtonIconRef,
      nextButtonTextRef,
      nextButtonIconRef,
      nextButtonColorRef,
      decrementPage,
      incrementPage,
    };
  }
});
</script>

<style lang="css" scoped>
.icon-primary {
  fill: var(--v-primary-base);
}

.icon-white {
  fill: white;
}

.icon-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  position: relative;
  margin-top: 2.5rem;
}

.icon-divider {
  width: 100%;
  margin-bottom: -2.5rem;
}

.icon-avatar {
  border-color: rgba(0, 0, 0, 0.12);
  border: 2px;
}

.bg-off-white {
  background: #f5f8fa;
}

.preferred-width {
  width: 840px;
}
</style>
