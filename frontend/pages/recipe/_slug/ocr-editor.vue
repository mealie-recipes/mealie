<template>
  <v-container
    v-if="recipe && recipe.slug && recipe.settings && recipe.recipeIngredient"
    :class="{
      'pa-0': $vuetify.breakpoint.smAndDown,
    }"
  >
    <BannerExperimental />

    <v-row v-if="!loading">
      <v-col cols="12" sm="7" md="7" lg="7">
        <v-card flat tile>
          <v-toolbar dense>
            <v-toolbar-title>Toolbar</v-toolbar-title>
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon>
                  <v-icon
                    :color="canvasMode === 'selection' ? 'primary' : 'default'"
                    v-bind="attrs"
                    @click="switchCanvasMode('selection')"
                    v-on="on"
                  >
                    {{ $globals.icons.selectMode }}
                  </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("ocr-editor.selection-mode") }}</span>
            </v-tooltip>
            <v-tooltip v-if="!isImageSmallerThanCanvas" bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon>
                  <v-icon
                    :color="canvasMode === 'panAndZoom' ? 'primary' : 'default'"
                    v-bind="attrs"
                    @click="switchCanvasMode('panAndZoom')"
                    v-on="on"
                  >
                    {{ $globals.icons.panAndZoom }}
                  </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("ocr-editor.pan-and-zoom-picture") }}</span>
            </v-tooltip>
            <v-divider vertical class="mx-2" />
            <v-toolbar-title>{{ $t("ocr-editor.split-text") }}</v-toolbar-title>
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon>
                  <v-icon
                    :color="selectedTextSplitMode === 'lineNum' ? 'primary' : 'default'"
                    v-bind="attrs"
                    @click="switchSplitTextMode('lineNum')"
                    v-on="on"
                  >
                    {{ $globals.icons.preserveLines }}
                  </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("ocr-editor.preserve-line-breaks") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon>
                  <v-icon
                    :color="selectedTextSplitMode === 'blockNum' ? 'primary' : 'default'"
                    v-bind="attrs"
                    @click="switchSplitTextMode('blockNum')"
                    v-on="on"
                  >
                    {{ $globals.icons.preserveBlocks }}
                  </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("ocr-editor.split-by-block") }}</span>
            </v-tooltip>
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon>
                  <v-icon
                    :color="selectedTextSplitMode === 'flatten' ? 'primary' : 'default'"
                    v-bind="attrs"
                    @click="switchSplitTextMode('flatten')"
                    v-on="on"
                  >
                    {{ $globals.icons.flatten }}
                  </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("ocr-editor.flatten") }}</span>
            </v-tooltip>

            <v-spacer></v-spacer>
            <BaseButton class="ml-1 mr-1" save @click="updateRecipe(recipe.slug, recipe)">
              {{ $t("general.save") }}
            </BaseButton>
            <BaseButton cancel @click="$router.push('/recipe/' + recipe.slug)">
              {{ $t("general.close") }}
            </BaseButton>
            <v-tooltip bottom>
              <template #activator="{ on, attrs }">
                <v-btn icon>
                  <v-icon v-bind="attrs" v-on="on" @click="showHelp = !showHelp"> {{ $globals.icons.help }} </v-icon>
                </v-btn>
              </template>
              <span>{{ $t("ocr-editor.help") }}</span>
            </v-tooltip>
          </v-toolbar>
          <canvas
            id="canvas"
            @mousedown="handleMouseDown"
            @mouseup="handleMouseUp"
            @mousemove="handleMouseMove"
            @wheel="handleMouseScroll"
          ></canvas>
          <span style="white-space: pre-wrap">
            {{ selectedText }}
          </span>
        </v-card>
      </v-col>
      <v-col cols="12" sm="5" md="5" lg="5">
        <v-tabs v-model="tab" fixed-tabs>
          <v-tab key="header">
            {{ $t("general.recipe") }}
          </v-tab>
          <v-tab key="ingredients">
            {{ $t("recipe.ingredients") }}
          </v-tab>
          <v-tab key="instructions">
            {{ $t("recipe.instructions") }}
          </v-tab>
        </v-tabs>
        <v-tabs-items v-model="tab">
          <v-tab-item key="header">
            <v-text-field
              v-model="recipe.name"
              class="my-3"
              :label="$t('recipe.recipe-name')"
              :rules="[validators.required]"
              @focus="selectedRecipeField = 'name'"
            >
            </v-text-field>

            <div class="d-flex flex-wrap">
              <v-text-field
                v-model="recipe.totalTime"
                class="mx-2"
                :label="$t('recipe.total-time')"
                @click="selectedRecipeField = 'totalTime'"
              ></v-text-field>
              <v-text-field
                v-model="recipe.prepTime"
                class="mx-2"
                :label="$t('recipe.prep-time')"
                @click="selectedRecipeField = 'prepTime'"
              ></v-text-field>
              <v-text-field
                v-model="recipe.performTime"
                class="mx-2"
                :label="$t('recipe.perform-time')"
                @click="selectedRecipeField = 'performTime'"
              ></v-text-field>
            </div>

            <v-textarea
              v-model="recipe.description"
              auto-grow
              min-height="100"
              :label="$t('recipe.description')"
              @click="selectedRecipeField = 'description'"
            >
            </v-textarea>
            <v-text-field
              v-model="recipe.recipeYield"
              dense
              :label="$t('recipe.servings')"
              @click="selectedRecipeField = 'recipeYield'"
            >
            </v-text-field>
          </v-tab-item>
          <v-tab-item key="ingredients">
            <div class="d-flex justify-end mt-2">
              <RecipeDialogBulkAdd class="ml-1 mr-1" :input-text-prop="selectedText" @bulk-data="addIngredient" />
              <BaseButton @click="addIngredient"> {{ $t("general.new") }} </BaseButton>
            </div>
            <draggable
              v-if="recipe.recipeIngredient.length > 0"
              v-model="recipe.recipeIngredient"
              handle=".handle"
              v-bind="{
                animation: 200,
                group: 'description',
                disabled: false,
                ghostClass: 'ghost',
              }"
              @start="drag = true"
              @end="drag = false"
            >
              <TransitionGroup type="transition" :name="!drag ? 'flip-list' : ''">
                <RecipeIngredientEditor
                  v-for="(ingredient, index) in recipe.recipeIngredient"
                  :key="ingredient.referenceId"
                  v-model="recipe.recipeIngredient[index]"
                  class="list-group-item"
                  :disable-amount="recipe.settings.disableAmount"
                  @delete="recipe.recipeIngredient.splice(index, 1)"
                  @clickIngredientField="setSingleIngredient($event, index)"
                />
              </TransitionGroup>
            </draggable>
          </v-tab-item>
          <v-tab-item key="instructions">
            <div class="d-flex justify-end mt-2">
              <RecipeDialogBulkAdd class="ml-1 mr-1" :input-text-prop="selectedText" @bulk-data="addStep" />
              <BaseButton @click="addStep()"> {{ $t("general.new") }}</BaseButton>
            </div>
            <RecipeInstructions
              v-model="recipe.recipeInstructions"
              :ingredients="recipe.recipeIngredient"
              :disable-amount="recipe.settings.disableAmount"
              :edit="true"
              :recipe-id="recipe.id"
              :recipe-slug="recipe.slug"
              :assets.sync="recipe.assets"
              @clickInstructionField="setSingleStep"
            />
          </v-tab-item>
        </v-tabs-items>
      </v-col>
    </v-row>
    <v-dialog v-model="showHelp" width="800px">
      <v-card>
        <v-app-bar dense dark color="primary" class="mb-2">
          <v-icon large left>
            {{ $globals.icons.help }}
          </v-icon>
          <v-toolbar-title class="headline"> Help </v-toolbar-title>
          <v-spacer></v-spacer>
        </v-app-bar>
        <v-card-text>
          <h1>Mouse modes</h1>
          <v-divider class="mb-2 mt-1" />
          <h2 class="my-2">
            <v-icon> {{ $globals.icons.selectMode }} </v-icon>{{ $t("ocr-editor.help-dialog.selection-mode") }}
          </h2>
          <p class="my-1">{{ $t("ocr-editor.help-dialog.selection-mode") }}</p>
          <ol>
            <li>{{ $t("ocr-editor.help-dialog.selection-mode-steps.draw") }}</li>
            <li>{{ $t("ocr-editor.help-dialog.selection-mode-steps.click") }}</li>
            <li>{{ $t("ocr-editor.help-dialog.selection-mode-steps.result") }}</li>
          </ol>
          <h2 class="my-2">
            <v-icon> {{ $globals.icons.panAndZoom }} </v-icon>{{ $t("ocr-editor.help-dialog.pan-and-zoom-mode") }}
          </h2>
          {{ $t("ocr-editor.help-dialog.pan-and-zoom-desc") }}
          <h1 class="mt-5">{{ $t("ocr-editor.help-dialog.split-text-mode") }}</h1>
          <v-divider class="mb-2 mt-1" />
          <h2 class="my-2">
            <v-icon> {{ $globals.icons.preserveLines }} </v-icon
            >{{ $t("ocr-editor.help-dialog.split-modes.line-mode") }}
          </h2>
          <p>
            {{ $t("ocr-editor.help-dialog.split-modes.line-mode-desc") }}
          </p>
          <h2 class="my-2">
            <v-icon> {{ $globals.icons.preserveBlocks }} </v-icon>
            {{ $t("ocr-editor.help-dialog.split-modes.block-mode") }}
          </h2>
          <p>
            {{ $t("ocr-editor.help-dialog.split-modes.block-mode-desc") }}
          </p>
          <h2 class="my-2">
            <v-icon> {{ $globals.icons.flatten }} </v-icon> {{ $t("ocr-editor.help-dialog.split-modes.flat-mode") }}
          </h2>
          <p>{{ $t("ocr-editor.help-dialog.split-modes.flat-mode-desc") }}</p>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import {
  defineComponent,
  useRoute,
  ref,
  onMounted,
  reactive,
  toRefs,
  useRouter,
  nextTick,
} from "@nuxtjs/composition-api";
import { until } from "@vueuse/core";
import { invoke } from "@vueuse/shared";
import draggable from "vuedraggable";
import { useUserApi, useStaticRoutes } from "~/composables/api";
import { useRecipe } from "~/composables/recipes";
import { OcrTsvResponse } from "~/types/api-types/ocr";
import { validators } from "~/composables/use-validators";
import { Recipe, RecipeIngredient, RecipeStep } from "~/types/api-types/recipe";
import BannerExperimental from "~/components/global/BannerExperimental.vue";
import RecipeDialogBulkAdd from "~/components/Domain/Recipe/RecipeDialogBulkAdd.vue";
import RecipeInstructions from "~/components/Domain/Recipe/RecipeInstructions.vue";
import RecipeIngredientEditor from "~/components/Domain/Recipe/RecipeIngredientEditor.vue";
import { uuid4 } from "~/composables/use-utils";

type CanvasRect = {
  startX: number;
  startY: number;
  w: number;
  h: number;
};

type ImagePosition = {
  sx: number;
  sy: number;
  sWidth: number;
  sHeight: number;
  dx: number;
  dy: number;
  dWidth: number;
  dHeight: number;
  scale: number;
  panStartPoint: {
    x: number;
    y: number;
  };
};

type Mouse = {
  current: {
    x: number;
    y: number;
  };
  down: boolean;
};

// https://stackoverflow.com/questions/58434389/typescript-deep-keyof-of-a-nested-object/58436959#58436959
type Prev = [never, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, ...0[]];

type Join<K, P> = K extends string | number
  ? P extends string | number
    ? `${K}${"" extends P ? "" : "."}${P}`
    : never
  : never;

type Paths<T, D extends number = 10> = [D] extends [never]
  ? never
  : T extends object
  ? {
      [K in keyof T]-?: K extends string | number ? `${K}` | Join<K, Paths<T[K], Prev[D]>> : never;
    }[keyof T]
  : "";

type Leaves<T, D extends number = 10> = [D] extends [never]
  ? never
  : T extends object
  ? { [K in keyof T]-?: Join<K, Leaves<T[K], Prev[D]>> }[keyof T]
  : "";

type SelectedRecipeLeaves = Leaves<Recipe>;

type CanvasModes = "selection" | "panAndZoom";

type SelectedTextSplitModes = keyof OcrTsvResponse | "flatten";

export default defineComponent({
  components: {
    RecipeIngredientEditor,
    draggable,
    BannerExperimental,
    RecipeDialogBulkAdd,
    RecipeInstructions,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const slug = route.value.params.slug;
    const api = useUserApi();

    const tsv = ref<OcrTsvResponse[]>([]);

    const { recipe, loading, fetchRecipe } = useRecipe(slug);

    const drag = ref(false);

    const { recipeAssetPath } = useStaticRoutes();

    function assetURL(assetName: string) {
      return recipeAssetPath(recipe.value?.id as string, assetName);
    }

    const state = reactive({
      loading: true,
      canvas: null as HTMLCanvasElement | null,
      ctx: null as CanvasRenderingContext2D | null,
      canvasRect: null as DOMRect | null,
      tab: null,
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
      selectedRecipeField: "" as SelectedRecipeLeaves | "",
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
      showHelp: false,
    });

    const setPropertyValueByPath = function <T extends Recipe>(object: T, path: Paths<T>, value: any) {
      const a = path.split(".");
      let nextProperty: any = object;
      for (let i = 0, n = a.length - 1; i < n; ++i) {
        const k = a[i];
        if (k in nextProperty) {
          nextProperty = nextProperty[k];
        } else {
          return;
        }
      }
      nextProperty[a[a.length - 1]] = value;
    };

    const image = new Image();

    function updateImageScale() {
      state.imagePosition.scale = state.imagePosition.dWidth / image.width;

      // force the original ratio to be respected
      state.imagePosition.dHeight = image.height * state.imagePosition.scale;

      // Don't let images bigger than the canvas be zoomed in more than 1:1 scale
      // Meaning only let images smaller than the canvas to have a scale > 1
      if (!state.isImageSmallerThanCanvas && state.imagePosition.scale > 1) {
        state.imagePosition.scale = 1;
      }
    }

    function findRecipeTitle() {
      // This function will find the title of a recipe with the assumption that the title has the biggest ratio of surface area on number of words on the image

      const filtered = tsv.value.filter((element) => element.level === 2 || element.level === 5);
      const blocks = [[]] as OcrTsvResponse[][];
      let blockNum = 1;
      filtered.forEach((element, index, array) => {
        if (index !== 0 && array[index - 1].blockNum !== element.blockNum) {
          blocks.push([]);
          blockNum = element.blockNum;
        }
        blocks[blockNum - 1].push(element);
      });

      let bestScore = 0;
      let bestBlock = blocks[0];
      blocks.forEach((element) => {
        // element[0] is the block declaration line containing the blocks total dimensions
        // element.lenght is the number of words (+ 2) contained in that block
        const elementScore = (element[0].height * element[0].width) / element.length; // Prettier is adding useless parenthesis for a mysterious reason
        const elementText = element.map((element) => element.text).join(""); // Identify empty blocks and don't count them
        if (elementScore > bestScore && elementText !== "") {
          bestBlock = element;
          bestScore = elementScore;
        }
      });

      return bestBlock
        .filter((element) => element.level === 5 && element.conf >= 40)
        .map((element) => {
          return element.text.trim();
        })
        .join(" ");
    }

    onMounted(() => {
      invoke(async () => {
        await until(recipe).not.toBeNull();

        if (!recipe.value || !recipe.value.assets || !recipe.value.slug) {
          return;
        }

        const assetName = recipe.value?.assets[0].fileName as string;
        const imagesrc = assetURL(assetName);
        image.src = imagesrc;

        const res = await api.ocr.assetToTsv(recipe.value.slug, assetName);
        tsv.value = res.data as OcrTsvResponse[];
        state.loading = false;

        if (recipe.value.name?.match(/New\sOCR\sRecipe(\s\([0-9]+\))?/g)) {
          recipe.value.name = findRecipeTitle();
        }

        nextTick(() => {
          state.canvas = <HTMLCanvasElement>document.getElementById("canvas");
          state.ctx = <CanvasRenderingContext2D>state.canvas.getContext("2d");
          state.ctx.imageSmoothingEnabled = false;
          state.canvasRect = state.canvas.getBoundingClientRect();

          state.canvas.width = state.canvasRect.width;
          if (image.width < state.canvas.width) {
            state.isImageSmallerThanCanvas = true;
          }
          state.imagePosition.dWidth = state.canvas.width;

          updateImageScale();
          state.canvas.height = Math.min(image.height * state.imagePosition.scale, 700); // Max height of 700px

          state.imagePosition.sWidth = image.width;
          state.imagePosition.sHeight = image.height;
          state.imagePosition.dWidth = state.canvas.width;
          drawImage(state.ctx);
          drawWordBoxesOnCanvas(tsv.value);
        });
      });
    });

    function drawImage(ctx: CanvasRenderingContext2D) {
      ctx.drawImage(
        image,
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

    function switchCanvasMode(mode: CanvasModes) {
      if (state.canvasRect === null || state.canvas === null) return;
      state.canvasMode = mode;
      if (mode === "panAndZoom") {
        state.canvas.style.cursor = "pointer";
      } else {
        state.canvas.style.cursor = "default";
      }
    }

    function switchSplitTextMode(mode: SelectedTextSplitModes) {
      if (state.canvasRect === null) return;
      state.selectedTextSplitMode = mode;
      state.selectedText = getWordsInSelection(tsv.value, state.rect);
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

    function handleMouseDown(event: MouseEvent) {
      if (state.canvasRect === null || state.canvas === null || state.ctx === null) return;
      state.mouse.down = true;

      updateMousePos(event);

      if (state.canvasMode === "selection") {
        if (isMouseInRect(state.mouse, state.rect)) {
          // Update the right field in the recipe

          if (state.selectedRecipeField !== "") {
            if (recipe.value === null) return;
            setPropertyValueByPath<Recipe>(recipe.value, state.selectedRecipeField, state.selectedText);
          }
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
      state.selectedText = getWordsInSelection(tsv.value, state.rect);
    }

    function keepImageInCanvas() {
      if (state.canvasRect === null || state.canvas === null) return;

      // Prevent image from being smaller than the canvas width
      if (state.imagePosition.dWidth - state.canvas.width < 0) {
        state.imagePosition.dWidth = state.canvas.width;
      }

      // Prevent image from being smaller than the canvas height
      if (state.imagePosition.dHeight - state.canvas.height < 0) {
        state.imagePosition.dHeight = image.height * state.imagePosition.scale;
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

        if (ndw < image.width) {
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

    function getWordsInSelection(tsv: OcrTsvResponse[], rect: CanvasRect) {
      const correctedRect = correctRectCoordinates(rect);

      return tsv
        .filter(
          (element) =>
            element.level === 5 &&
            correctedRect.startY - state.imagePosition.dy < element.top * state.imagePosition.scale &&
            correctedRect.startX - state.imagePosition.dx < element.left * state.imagePosition.scale &&
            correctedRect.startX + correctedRect.w >
              (element.left + element.width) * state.imagePosition.scale + state.imagePosition.dx &&
            correctedRect.startY + correctedRect.h >
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
          return element.text + separator;
        })
        .join("");
    }

    function addIngredient(ingredients: Array<string> | null = null) {
      if (ingredients?.length) {
        const newIngredients = ingredients.map((x) => {
          return {
            referenceId: uuid4(),
            title: "",
            note: x,
            unit: undefined,
            food: undefined,
            disableAmount: true,
            quantity: 1,
          };
        });

        if (newIngredients) {
          recipe?.value?.recipeIngredient?.push(...newIngredients);
        }
      } else {
        recipe?.value?.recipeIngredient?.push({
          referenceId: uuid4(),
          title: "",
          note: "",
          unit: undefined,
          food: undefined,
          disableAmount: true,
          quantity: 1,
        });
      }
    }

    function addStep(steps: Array<string> | null = null) {
      if (!recipe.value?.recipeInstructions) {
        return;
      }

      if (steps) {
        const cleanedSteps = steps.map((step) => {
          return { id: uuid4(), text: step, title: "", ingredientReferences: [] };
        });

        recipe.value.recipeInstructions.push(...cleanedSteps);
      } else {
        recipe.value.recipeInstructions.push({ id: uuid4(), text: "", title: "", ingredientReferences: [] });
      }
    }

    async function updateRecipe(slug: string, recipe: Recipe) {
      const { data } = await api.recipes.updateOne(slug, recipe);
      if (data?.slug) {
        router.push("/recipe/" + data.slug);
      }
    }

    function setSingleIngredient(f: keyof RecipeIngredient, index: number) {
      state.selectedRecipeField = `recipeIngredient.${index}.${f}` as SelectedRecipeLeaves;
    }

    // Leaves<RecipeStep[]> will return some function types making eslint very unhappy
    type RecipeStepsLeaves = `${number}.${Leaves<RecipeStep>}`;

    function setSingleStep(path: RecipeStepsLeaves) {
      state.selectedRecipeField = `recipeInstructions.${path}` as SelectedRecipeLeaves;
    }

    return {
      ...toRefs(state),
      addIngredient,
      addStep,
      api,
      recipe,
      loading,
      fetchRecipe,
      drag,
      assetURL,
      handleMouseDown,
      handleMouseUp,
      handleMouseMove,
      handleMouseScroll,
      updateRecipe,
      tsv,
      validators,
      switchCanvasMode,
      setSingleIngredient,
      setSingleStep,
      switchSplitTextMode,
    };
  },
});
</script>

<style lang="css">
.ghost {
  opacity: 0.5;
}

body {
  background: #eee;
}

canvas {
  background: white;
  box-shadow: 0px 2px 3px rgba(0, 0, 0, 0.2);
  width: 100%;
  image-rendering: optimizeQuality;
}
.box {
  position: absolute;
  border: 2px #90ee90 solid;
  background-color: #90ee90;

  z-index: 3;
}
</style>
