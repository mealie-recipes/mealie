<template>
    <div class="d-flex" :class="{ 'flex-column': useMobileFormat, 'flex-row': !useMobileFormat  }">
        <button v-if="useMobileFormat" class="scroll-arrow scroll-up hidden" @click="scrollVert(false)">Up</button>
        <button v-else class="scroll-arrow scroll-left" @click="scrollHoriz(false)">
            <v-icon> {{ $globals.icons.arrowLeftBold }} </v-icon>
        </button>
        <div ref="mealplan-container" class="mealplan-container" :class="{ 'flex-column': useMobileFormat, 'flex-row': !useMobileFormat  }">
            <slot></slot>
        </div>
        <button v-if="useMobileFormat" class="scroll-arrow scroll-down hidden" @click="scrollVert(true)">Down</button>
        <button v-else class="scroll-arrow scroll-right" @click="scrollHoriz(true)">
            <v-icon> {{ $globals.icons.arrowRightBold }} </v-icon>
        </button>
    </div>
</template>

<script lang="ts">
import { defineComponent, computed, useContext } from "@nuxtjs/composition-api";

export default defineComponent({
    props: {
        getDaysRefs: {
            type: Function,
            default(rawProps: () => HTMLDivElement[] | undefined) {
                return rawProps();
            },
            required: true
        }
    },
    setup(props) {
        const { $vuetify } = useContext();
        const useMobileFormat = computed(() => {
            return $vuetify.breakpoint.smAndDown;
        });
        const getRefs = (props.getDaysRefs as () => HTMLDivElement[] | undefined);

        return {
            useMobileFormat,
            getRefs,
        };
    },
    methods: {
        scrollHoriz(forward?: boolean) {
            const daysRefs = this.getRefs();
            if(daysRefs && this.$refs["mealplan-container"]) {
                const containerRef = this.$refs["mealplan-container"] as HTMLDivElement

                const getOffset = (el: HTMLDivElement) => el.offsetLeft;

                const getScroll = (el: HTMLDivElement) => el.scrollLeft;

                const containerOffset = getOffset(containerRef);
                let scrollDist: number[] = daysRefs.map((day) => getOffset(day) - getScroll(containerRef) - containerOffset);

                if(forward) {
                scrollDist = scrollDist.filter(n => n > 0);
                scrollDist.sort((a,b) => a-b);
                } else {
                scrollDist = scrollDist.filter(n => n < 0);
                scrollDist.sort((a,b) => b-a);
                }

                containerRef.scrollTo({
                left: scrollDist[0] + getScroll(containerRef) ,
                behavior: "smooth"
                });
            } else {
                console.log("Unable to perform scrolling due to missing ref")
            }
        },
        scrollVert(forward?: boolean) {
            const daysRefs = this.getRefs();
            if(daysRefs && this.$refs["mealplan-container"]) {
                const containerRef = this.$refs["mealplan-container"] as HTMLDivElement

                const getOffset = (el: HTMLDivElement) => el.offsetTop ;

                let scrollDist: number[] = daysRefs.map((day) => getOffset(day) - window.scrollY);

                if(forward) {
                scrollDist = scrollDist.filter(n => n > 0);
                scrollDist.sort((a,b) => a-b);
                } else {
                scrollDist = scrollDist.filter(n => n < 0);
                scrollDist.sort((a,b) => b-a);
                }

                window.scrollTo({
                top: scrollDist[0] + window.scrollY ,
                behavior: "smooth"
                });
            } else {
                console.log("Unable to perform scrolling due to missing ref")
            }
        }
    },
});
</script>

<style>
.mealplan-container {
display: flex;
margin: -12px 12px -12px 12px;
overflow: scroll;
overflow-y: hidden;
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none;  /* Internet Explorer 10+ */
}

.mealplan-container::-webkit-scrollbar { /* WebKit */
    width: 0;
    height: 0;
}

.scroll-right, .scroll-left {
position: relative;
top: 12px;
align-self: baseline;
}

.scroll-up {
position: fixed;
top: 50px;
align-self: center;
z-index: 999;
}

.scroll-down {
position: fixed;
bottom: 0px;
align-self: center;
z-index: 999;
}

</style>
