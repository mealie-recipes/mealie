  <template>
  <v-menu offset-y>
    <template #activator="{ on, attrs }">
      <v-btn color="primary" v-bind="attrs" :class="btnClass" v-on="on">
        <v-icon v-if="activeObj.icon" left>
          {{ activeObj.icon }}
        </v-icon>
        {{ activeObj.text }}
        <v-icon right>
          {{ $globals.icons.chevronDown }}
        </v-icon>
      </v-btn>
    </template>
    <v-list>
      <v-list-item-group v-model="itemGroup">
        <v-list-item v-for="(item, index) in items" :key="index" @click="setValue(item)">
          <v-list-item-icon v-if="item.icon">
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
          <v-list-item-title>{{ item.text }}</v-list-item-title>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-menu>
</template>

<script lang="ts">
import { defineComponent, ref } from "@nuxtjs/composition-api";

const INPUT_EVENT = "input";

export default defineComponent({
  props: {
    items: {
      type: Array,
      required: true,
    },
    value: {
      type: String,
      required: false,
      default: "",
    },
    btnClass: {
      type: String,
      required: false,
      default: "",
    },
  },
  setup(props, context) {
    const activeObj = ref({
      text: "DEFAULT",
      value: "",
    });

    let startIndex = 0;
    props.items.forEach((item, index) => {
      // @ts-ignore
      if (item.value === props.value) {
        startIndex = index;

        // @ts-ignore
        activeObj.value = item;
      }
    });
    const itemGroup = ref(startIndex);

    function setValue(v: any) {
      context.emit(INPUT_EVENT, v.value);
      activeObj.value = v;
    }

    return {
      activeObj,
      itemGroup,
      setValue,
    };
  },
});
</script>


    