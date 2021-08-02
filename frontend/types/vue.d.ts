import Vue from "vue";

declare module "vue/types/vue" {

    interface Vue {
        $globals: any;
    }
}

declare module "vue/types/options" {
    interface ComponentOptions<V extends Vue> {
        $globals?: any;
    }
}
