<template>
  <v-card flat tile>
    <v-toolbar v-for="(section, idx) in toolbarIcons" :key="section.sectionTitle" dense style="float: left">
      <v-toolbar-title bottom>
        {{ section.sectionTitle }}
      </v-toolbar-title>
      <v-tooltip v-for="icon in section.icons" :key="icon.name" bottom>
        <template #activator="{ on, attrs }">
          <v-btn icon @click="section.eventHandler(icon.name)">
            <v-icon :color="section.highlight === icon.name ? 'primary' : 'default'" v-bind="attrs" v-on="on">
              {{ icon.icon }}
            </v-icon>
          </v-btn>
        </template>
        <span>{{ icon.tooltip }}</span>
      </v-tooltip>
      <v-divider v-if="idx != toolbarIcons.length - 1" vertical class="mx-2" />
    </v-toolbar>
    <v-toolbar dense style="float: right">
      <BaseButton class="ml-1 mr-1" save @click="updateRecipe()">
        {{ $t("general.save") }}
      </BaseButton>
      <BaseButton cancel @click="closeEditor()">
        {{ $t("general.close") }}
      </BaseButton>
    </v-toolbar>
    <canvas
      ref="canvas"
      @mousedown="handleMouseDown"
      @mouseup="handleMouseUp"
      @mousemove="handleMouseMove"
      @wheel="handleMouseScroll"
    >
    </canvas>
    <span style="white-space: pre-wrap">
      {{ selectedText.trim() }}
    </span>
  </v-card>
</template>

<script lang="ts">
import { defineComponent, reactive, useContext, ref, toRefs, watch } from "@nuxtjs/composition-api";
import { onMounted } from "vue-demi";
import { NoUndefinedField } from "~/lib/api/types/non-generated";
import { OcrTsvResponse as NullableOcrTsvResponse } from "~/lib/api/types/ocr";
import { CanvasModes, SelectedTextSplitModes, ImagePosition, Mouse, CanvasRect, ToolbarIcons } from "~/types/ocr-types";

// Temporary Shim until we have a better solution
// https://github.com/phillipdupuis/pydantic-to-typescript/issues/28
type OcrTsvResponse = NoUndefinedField<NullableOcrTsvResponse>;

export default defineComponent({
  props: {
    image: {
      type: HTMLImageElement,
      required: true,
    },
    tsv: {
      type: Array as () => OcrTsvResponse[],
      required: true,
    },
  },
  setup(props, context) {
    const state = reactive({
      canvas: null as HTMLCanvasElement | null,
      ctx: null as CanvasRenderingContext2D | null,
      canvasRect: null as DOMRect | null,
      rect: {
        startX: 0,
        startY: 0,
        w: 0,
        h: 0,
      },
      mouse: {
        current: {
          x: 0,
          y: 0,
        },
        down: false,
      },
      selectedText: "",
      canvasMode: "selection" as CanvasModes,
      imagePosition: {
        sx: 0,
        sy: 0,
        sWidth: 0,
        sHeight: 0,
        dx: 0,
        dy: 0,
        dWidth: 0,
        dHeight: 0,
        scale: 1,
        panStartPoint: {
          x: 0,
          y: 0,
        },
      } as ImagePosition,
      isImageSmallerThanCanvas: false,
      selectedTextSplitMode: "lineNum" as SelectedTextSplitModes,
    });

    watch(
      () => state.selectedText,
      (value) => {
        context.emit("text-selected", value);
      }
    );

    onMounted(() => {
      if (state.canvas === null) return; // never happens because the ref "canvas" is in the template
      state.ctx = state.canvas.getContext("2d") as CanvasRenderingContext2D;
      state.ctx.imageSmoothingEnabled = false;
      state.canvasRect = state.canvas.getBoundingClientRect();

      state.canvas.width = state.canvasRect.width;
      if (props.image.width < state.canvas.width) {
        state.isImageSmallerThanCanvas = true;
      }
      state.imagePosition.dWidth = state.canvas.width;

      updateImageScale();
      state.canvas.height = Math.min(props.image.height * state.imagePosition.scale, 700); // Max height of 700px

      state.imagePosition.sWidth = props.image.width;
      state.imagePosition.sHeight = props.image.height;
      state.imagePosition.dWidth = state.canvas.width;
      drawImage(state.ctx);
      drawWordBoxesOnCanvas(props.tsv);
    });

    function handleMouseDown(event: MouseEvent) {
      if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;
      state.mouse.down = true;

      updateMousePos(event);

      if (state.canvasMode === "selection") {
        if (isMouseInRect(state.mouse, state.rect)) {
          context.emit("setText", state.selectedText);
        } else {
          state.ctx.fillStyle = "rgb(255, 255, 255)";
          state.ctx.fillRect(0, 0, state.canvas.width, state.canvas.height);
          drawImage(state.ctx);
          state.rect.startX = state.mouse.current.x;
          state.rect.startY = state.mouse.current.y;
          resetSelection();
        }
        return;
      }

      if (state.canvasMode === "panAndZoom") {
        state.imagePosition.panStartPoint.x = state.mouse.current.x - state.imagePosition.dx;
        state.imagePosition.panStartPoint.y = state.mouse.current.y - state.imagePosition.dy;
        resetSelection();
      }
    }

    function handleMouseUp(_event: MouseEvent) {
      if (state.canvasRect === null) return;
      state.mouse.down = false;
      state.selectedText = getWordsInSelection(props.tsv, state.rect);
    }

    function handleMouseMove(event: MouseEvent) {
      if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;

      updateMousePos(event);

      if (state.mouse.down) {
        if (state.canvasMode === "selection") {
          state.rect.w = state.mouse.current.x - state.rect.startX;
          state.rect.h = state.mouse.current.y - state.rect.startY;
          draw();
          return;
        }

        if (state.canvasMode === "panAndZoom") {
          state.canvas.style.cursor = "move";
          state.imagePosition.dx = state.mouse.current.x - state.imagePosition.panStartPoint.x;
          state.imagePosition.dy = state.mouse.current.y - state.imagePosition.panStartPoint.y;
          keepImageInCanvas();
          state.ctx.fillStyle = "rgb(255, 255, 255)";
          state.ctx.fillRect(0, 0, state.canvas.width, state.canvas.height);
          drawImage(state.ctx);
          return;
        }
      }

      if (isMouseInRect(state.mouse, state.rect) && state.canvasMode === "selection") {
        state.canvas.style.cursor = "pointer";
      } else {
        state.canvas.style.cursor = "default";
      }
    }

    const scrollSensitivity = 0.05;

    function handleMouseScroll(event: WheelEvent) {
      if (state.isImageSmallerThanCanvas) return;
      if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;

      if (state.canvasMode === "panAndZoom") {
        event.preventDefault();

        updateMousePos(event);

        const m = Math.sign(event.deltaY);

        const ndx = state.imagePosition.dx + m * state.imagePosition.dWidth * scrollSensitivity;
        const ndy = state.imagePosition.dy + m * state.imagePosition.dHeight * scrollSensitivity;
        const ndw = state.imagePosition.dWidth + -m * state.imagePosition.dWidth * scrollSensitivity * 2;
        const ndh = state.imagePosition.dHeight + -m * state.imagePosition.dHeight * scrollSensitivity * 2;

        if (ndw < props.image.width) {
          state.imagePosition.dx = ndx;
          state.imagePosition.dy = ndy;
          state.imagePosition.dWidth = ndw;
          state.imagePosition.dHeight = ndh;
        }

        keepImageInCanvas();
        updateImageScale();

        state.ctx.fillStyle = "rgb(255, 255, 255)";
        state.ctx.fillRect(0, 0, state.canvas.width, state.canvas.height);
        drawImage(state.ctx);
      }
    }

    function draw() {
      if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;
      if (state.mouse.down) {
        state.ctx.imageSmoothingEnabled = false;
        state.ctx.fillStyle = "rgb(255, 255, 255)";
        state.ctx.fillRect(0, 0, state.canvas.width, state.canvas.height);
        drawImage(state.ctx);
        state.ctx.fillStyle = "rgba(255, 255, 255, 0.1)";
        state.ctx.setLineDash([6]);
        state.ctx.fillRect(state.rect.startX, state.rect.startY, state.rect.w, state.rect.h);
        state.ctx.strokeRect(state.rect.startX, state.rect.startY, state.rect.w, state.rect.h);
      }
    }

    function drawImage(ctx: CanvasRenderingContext2D) {
      ctx.drawImage(
        props.image,
        state.imagePosition.sx,
        state.imagePosition.sy,
        state.imagePosition.sWidth,
        state.imagePosition.sHeight,
        state.imagePosition.dx,
        state.imagePosition.dy,
        state.imagePosition.dWidth,
        state.imagePosition.dHeight
      );
    }

    function keepImageInCanvas() {
      if (state.canvasRect === null || state.canvas === null) return;

      // Prevent image from being smaller than the canvas width
      if (state.imagePosition.dWidth - state.canvas.width < 0) {
        state.imagePosition.dWidth = state.canvas.width;
      }

      // Prevent image from being smaller than the canvas height
      if (state.imagePosition.dHeight - state.canvas.height < 0) {
        state.imagePosition.dHeight = props.image.height * state.imagePosition.scale;
      }

      // Prevent to move the image too much to the left
      if (state.canvas.width - state.imagePosition.dx - state.imagePosition.dWidth > 0) {
        state.imagePosition.dx = state.canvas.width - state.imagePosition.dWidth;
      }

      // Prevent to move the image too much to the top
      if (state.canvas.height - state.imagePosition.dy - state.imagePosition.dHeight > 0) {
        state.imagePosition.dy = state.canvas.height - state.imagePosition.dHeight;
      }

      // Prevent to move the image too much to the right
      if (state.imagePosition.dx > 0) {
        state.imagePosition.dx = 0;
      }

      // Prevent to move the image too much to the bottom
      if (state.imagePosition.dy > 0) {
        state.imagePosition.dy = 0;
      }
    }

    function updateImageScale() {
      state.imagePosition.scale = state.imagePosition.dWidth / props.image.width;

      // force the original ratio to be respected
      state.imagePosition.dHeight = props.image.height * state.imagePosition.scale;

      // Don't let images bigger than the canvas be zoomed in more than 1:1 scale
      // Meaning only let images smaller than the canvas to have a scale > 1
      if (!state.isImageSmallerThanCanvas && state.imagePosition.scale > 1) {
        state.imagePosition.scale = 1;
      }
    }

    function resetSelection() {
      if (state.canvasRect === null) return;
      state.rect.w = 0;
      state.rect.h = 0;
      state.selectedText = "";
    }

    function updateMousePos<T extends MouseEvent>(event: T) {
      if (state.canvas === null) return;
      state.canvasRect = state.canvas.getBoundingClientRect();
      state.mouse.current = {
        x: event.clientX - state.canvasRect.left,
        y: event.clientY - state.canvasRect.top,
      };
    }

    function isMouseInRect(mouse: Mouse, rect: CanvasRect) {
      if (state.canvasRect === null) return;
      const correctRect = correctRectCoordinates(rect);

      return (
        mouse.current.x > correctRect.startX &&
        mouse.current.x < correctRect.startX + correctRect.w &&
        mouse.current.y > correctRect.startY &&
        mouse.current.y < correctRect.startY + correctRect.h
      );
    }

    /**
     * Returns rectangle coordinates with positive dimensions
     * @param  rect  A rectangle
     * @returns  An equivalent rectangle with width and height > 0
     */
    function correctRectCoordinates(rect: CanvasRect) {
      if (rect.w < 0) {
        rect.startX = rect.startX + rect.w;
        rect.w = -rect.w;
      }

      if (rect.h < 0) {
        rect.startY = rect.startY + rect.h;
        rect.h = -rect.h;
      }
      return rect;
    }

    function drawWordBoxesOnCanvas(tsv: OcrTsvResponse[]) {
      if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;

      state.ctx.fillStyle = "rgb(255, 255, 255, 0.3)";
      tsv
        .filter((element) => element.level === 5)
        .forEach((element) => {
          if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;
          state.ctx.fillRect(
            element.left * state.imagePosition.scale,
            element.top * state.imagePosition.scale,
            element.width * state.imagePosition.scale,
            element.height * state.imagePosition.scale
          );
        });
    }

    // Event emitters
    const updateRecipe = function () {
      context.emit("update-recipe");
    };

    const closeEditor = function () {
      context.emit("close-editor");
    };

    // TOOLBAR STUFF

    const { $globals, i18n } = useContext();

    const toolbarIcons = ref<ToolbarIcons<CanvasModes | SelectedTextSplitModes>>([
      {
        sectionTitle: "Toolbar",
        eventHandler: switchCanvasMode,
        highlight: state.canvasMode,
        icons: [
          {
            name: "selection",
            icon: $globals.icons.selectMode,
            tooltip: i18n.tc("ocr-editor.selection-mode"),
          },
          {
            name: "panAndZoom",
            icon: $globals.icons.panAndZoom,
            tooltip: i18n.tc("ocr-editor.pan-and-zoom-picture"),
          },
        ],
      },
      {
        sectionTitle: i18n.tc("ocr-editor.split-text"),
        eventHandler: switchSplitTextMode,
        highlight: state.selectedTextSplitMode,
        icons: [
          {
            name: "lineNum",
            icon: $globals.icons.preserveLines,
            tooltip: i18n.tc("ocr-editor.preserve-line-breaks"),
          },
          {
            name: "blockNum",
            icon: $globals.icons.preserveBlocks,
            tooltip: i18n.tc("ocr-editor.split-by-block"),
          },
          {
            name: "flatten",
            icon: $globals.icons.flatten,
            tooltip: i18n.tc("ocr-editor.flatten"),
          },
        ],
      },
    ]);

    function switchCanvasMode(mode: CanvasModes) {
      if (state.canvasRect === null || state.canvas === null) return;
      state.canvasMode = mode;
      toolbarIcons.value[0].highlight = mode;
      if (mode === "panAndZoom") {
        state.canvas.style.cursor = "pointer";
      } else {
        state.canvas.style.cursor = "default";
      }
    }

    function switchSplitTextMode(mode: SelectedTextSplitModes) {
      if (state.canvasRect === null) return;
      state.selectedTextSplitMode = mode;
      toolbarIcons.value[1].highlight = mode;
      state.selectedText = getWordsInSelection(props.tsv, state.rect);
    }

    /**
     * Using rectangle coordinates, filters the tsv to get text elements contained
     * inside the rectangle
     * Additionaly adds newlines depending on the current "text split" mode
     * @param  tsv   An Object containing tesseracts tsv fields
     * @param  rect  Coordinates of a rectangle
     * @returns Text from tsv contained in the rectangle
     */
    function getWordsInSelection(tsv: OcrTsvResponse[], rect: CanvasRect) {
      const correctedRect = correctRectCoordinates(rect);

      return tsv
        .filter(
          (element) =>
            element.level === 5 &&
            correctedRect.startY - state.imagePosition.dy < element.top * state.imagePosition.scale &&
            correctedRect.startX - state.imagePosition.dx < element.left * state.imagePosition.scale &&
            correctedRect.startX + correctedRect.w >
              // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
              (element.left + element.width) * state.imagePosition.scale + state.imagePosition.dx &&
            correctedRect.startY + correctedRect.h >
              // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
              (element.top + element.height) * state.imagePosition.scale + state.imagePosition.dy
        )
        .map((element, index, array) => {
          let separator = " ";
          if (
            state.selectedTextSplitMode !== "flatten" &&
            index !== array.length - 1 &&
            element[state.selectedTextSplitMode] !== array[index + 1][state.selectedTextSplitMode]
          ) {
            separator = "\n";
          }
          // eslint-disable-next-line @typescript-eslint/restrict-plus-operands
          return element.text + separator;
        })
        .join("");
    }

    return {
      ...toRefs(state),
      handleMouseDown,
      handleMouseUp,
      handleMouseMove,
      handleMouseScroll,
      toolbarIcons,
      updateRecipe,
      closeEditor,
    };
  },
});
</script>
