(function (e) {
  function t(t) {
    for (
      var n, s, c = t[0], o = t[1], l = t[2], d = 0, p = [];
      d < c.length;
      d++
    )
      (s = c[d]),
        Object.prototype.hasOwnProperty.call(i, s) && i[s] && p.push(i[s][0]),
        (i[s] = 0);
    for (n in o) Object.prototype.hasOwnProperty.call(o, n) && (e[n] = o[n]);
    u && u(t);
    while (p.length) p.shift()();
    return r.push.apply(r, l || []), a();
  }
  function a() {
    for (var e, t = 0; t < r.length; t++) {
      for (var a = r[t], n = !0, c = 1; c < a.length; c++) {
        var o = a[c];
        0 !== i[o] && (n = !1);
      }
      n && (r.splice(t--, 1), (e = s((s.s = a[0]))));
    }
    return e;
  }
  var n = {},
    i = { app: 0 },
    r = [];
  function s(t) {
    if (n[t]) return n[t].exports;
    var a = (n[t] = { i: t, l: !1, exports: {} });
    return e[t].call(a.exports, a, a.exports, s), (a.l = !0), a.exports;
  }
  (s.m = e),
    (s.c = n),
    (s.d = function (e, t, a) {
      s.o(e, t) || Object.defineProperty(e, t, { enumerable: !0, get: a });
    }),
    (s.r = function (e) {
      "undefined" !== typeof Symbol &&
        Symbol.toStringTag &&
        Object.defineProperty(e, Symbol.toStringTag, { value: "Module" }),
        Object.defineProperty(e, "__esModule", { value: !0 });
    }),
    (s.t = function (e, t) {
      if ((1 & t && (e = s(e)), 8 & t)) return e;
      if (4 & t && "object" === typeof e && e && e.__esModule) return e;
      var a = Object.create(null);
      if (
        (s.r(a),
        Object.defineProperty(a, "default", { enumerable: !0, value: e }),
        2 & t && "string" != typeof e)
      )
        for (var n in e)
          s.d(
            a,
            n,
            function (t) {
              return e[t];
            }.bind(null, n)
          );
      return a;
    }),
    (s.n = function (e) {
      var t =
        e && e.__esModule
          ? function () {
              return e["default"];
            }
          : function () {
              return e;
            };
      return s.d(t, "a", t), t;
    }),
    (s.o = function (e, t) {
      return Object.prototype.hasOwnProperty.call(e, t);
    }),
    (s.p = "/static/");
  var c = (window["webpackJsonp"] = window["webpackJsonp"] || []),
    o = c.push.bind(c);
  (c.push = t), (c = c.slice());
  for (var l = 0; l < c.length; l++) t(c[l]);
  var u = o;
  r.push([0, "chunk-vendors"]), a();
})({
  0: function (e, t, a) {
    e.exports = a("56d7");
  },
  "0d48": function (e, t, a) {
    "use strict";
    a("1e26");
  },
  "1e26": function (e, t, a) {},
  "56d7": function (e, t, a) {
    "use strict";
    a.r(t);
    a("4de4"), a("fb6a"), a("e260"), a("e6cf"), a("cca6"), a("a79d");
    var n = a("2b0e"),
      i = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "v-app",
          [
            a(
              "v-app-bar",
              {
                attrs: {
                  dense: "",
                  app: "",
                  color: "primary darken-3",
                  dark: "",
                },
              },
              [
                a("router-link", { attrs: { to: "/" } }),
                a(
                  "div",
                  { staticClass: "d-flex align-center" },
                  [
                    a(
                      "v-icon",
                      {
                        attrs: { size: "40" },
                        on: {
                          click: function (t) {
                            return e.$router.push("/");
                          },
                        },
                      },
                      [e._v(" mdi-food-variant")]
                    ),
                  ],
                  1
                ),
                a(
                  "div",
                  { staticClass: "pl-2" },
                  [
                    a(
                      "v-toolbar-title",
                      {
                        on: {
                          click: function (t) {
                            return e.$router.push("/");
                          },
                        },
                      },
                      [e._v("Mealie")]
                    ),
                  ],
                  1
                ),
                a("v-spacer"),
              ],
              1
            ),
            a(
              "v-main",
              [a("v-container", [a("AddRecipe"), a("router-view")], 1)],
              1
            ),
          ],
          1
        );
      },
      r = [],
      s = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "div",
          { staticClass: "text-center" },
          [
            a(
              "v-dialog",
              {
                attrs: { width: "650" },
                model: {
                  value: e.addRecipe,
                  callback: function (t) {
                    e.addRecipe = t;
                  },
                  expression: "addRecipe",
                },
              },
              [
                a(
                  "v-card",
                  { attrs: { loading: e.processing } },
                  [
                    a("v-card-title", { staticClass: "headline" }, [
                      e._v(" From URL "),
                    ]),
                    a(
                      "v-card-text",
                      [
                        a(
                          "v-form",
                          [
                            a("v-text-field", {
                              attrs: { label: "Recipe URL" },
                              model: {
                                value: e.recipeURL,
                                callback: function (t) {
                                  e.recipeURL = t;
                                },
                                expression: "recipeURL",
                              },
                            }),
                          ],
                          1
                        ),
                      ],
                      1
                    ),
                    a("v-divider"),
                    a(
                      "v-card-actions",
                      [
                        a("v-spacer"),
                        a(
                          "v-btn",
                          {
                            attrs: { color: "primary", text: "" },
                            on: { click: e.createRecipe },
                          },
                          [e._v(" Submit ")]
                        ),
                      ],
                      1
                    ),
                  ],
                  1
                ),
              ],
              1
            ),
            a(
              "v-speed-dial",
              {
                attrs: {
                  fixed: "",
                  right: "",
                  bottom: "",
                  "open-on-hover": "",
                },
                scopedSlots: e._u([
                  {
                    key: "activator",
                    fn: function () {
                      return [
                        a(
                          "v-btn",
                          {
                            attrs: {
                              color: "primary darken-2",
                              dark: "",
                              fab: "",
                            },
                            on: { click: e.navCreate },
                            model: {
                              value: e.fab,
                              callback: function (t) {
                                e.fab = t;
                              },
                              expression: "fab",
                            },
                          },
                          [a("v-icon", [e._v(" mdi-plus ")])],
                          1
                        ),
                      ];
                    },
                    proxy: !0,
                  },
                ]),
                model: {
                  value: e.fab,
                  callback: function (t) {
                    e.fab = t;
                  },
                  expression: "fab",
                },
              },
              [
                a(
                  "v-btn",
                  {
                    attrs: { fab: "", dark: "", small: "", color: "green" },
                    on: {
                      click: function (t) {
                        e.addRecipe = !0;
                      },
                    },
                  },
                  [a("v-icon", [e._v("mdi-link")])],
                  1
                ),
              ],
              1
            ),
          ],
          1
        );
      },
      c = [],
      o = (a("96cf"), a("1da1")),
      l = a("bc3a"),
      u = a.n(l),
      d = "/api/recipe/create-url/",
      p = {
        data: function () {
          return { fab: !1, addRecipe: !1, recipeURL: "", processing: !1 };
        },
        methods: {
          createRecipe: function () {
            var e = this;
            return Object(o["a"])(
              regeneratorRuntime.mark(function t() {
                var a, n, i;
                return regeneratorRuntime.wrap(function (t) {
                  while (1)
                    switch ((t.prev = t.next)) {
                      case 0:
                        return (
                          (e.processing = !0),
                          (a = { url: e.recipeURL }),
                          (t.next = 4),
                          u.a.post(d, a)
                        );
                      case 4:
                        (n = t.sent),
                          (i = n.data),
                          (e.addRecipe = !1),
                          (e.processing = !1),
                          e.$store.commit("setRenderRecipes", !0),
                          e.$router.push("/recipe/".concat(i));
                      case 10:
                      case "end":
                        return t.stop();
                    }
                }, t);
              })
            )();
          },
          navCreate: function () {
            this.$router.push("/new");
          },
        },
      },
      v = p,
      f = a("2877"),
      m = a("6544"),
      h = a.n(m),
      g = a("8336"),
      b = a("b0af"),
      _ = a("99d9"),
      x = a("169a"),
      R = a("ce7e"),
      k = a("4bd4"),
      C = a("132d"),
      V = a("2fa4"),
      w = a("c73b"),
      y = a("8654"),
      S = Object(f["a"])(v, s, c, !1, null, null, null),
      j = S.exports;
    h()(S, {
      VBtn: g["a"],
      VCard: b["a"],
      VCardActions: _["a"],
      VCardText: _["b"],
      VCardTitle: _["c"],
      VDialog: x["a"],
      VDivider: R["a"],
      VForm: k["a"],
      VIcon: C["a"],
      VSpacer: V["a"],
      VSpeedDial: w["a"],
      VTextField: y["a"],
    });
    var I = {
        name: "App",
        components: { AddRecipe: j },
        data: function () {
          return {};
        },
        computed: {
          showRecipe: function () {
            return this.$store.getters.getShowRecipe;
          },
        },
      },
      D = I,
      $ = a("7496"),
      O = a("40dc"),
      E = a("a523"),
      A = a("f6c4"),
      T = a("2a7f"),
      U = Object(f["a"])(D, i, r, !1, null, null, null),
      F = U.exports;
    h()(U, {
      VApp: $["a"],
      VAppBar: O["a"],
      VContainer: E["a"],
      VIcon: C["a"],
      VMain: A["a"],
      VSpacer: V["a"],
      VToolbarTitle: T["a"],
    });
    var L = a("f309");
    n["a"].use(L["a"]);
    var M = new L["a"]({}),
      N = a("2f62");
    n["a"].use(N["a"]);
    var P = new N["a"].Store({
        state: {
          renderRecipes: !1,
          showRecipe: !1,
          activeRecipe: "String",
          saveRecipe: !1,
        },
        mutations: {
          setRenderRecipes: function (e, t) {
            e.renderRecipes = t;
          },
          setShowRecipe: function (e, t) {
            e.showRecipe = t;
          },
          setSaveRecipe: function (e, t) {
            (e.saveRecipe = t), console.log(e.saveRecipe);
          },
          setActiveRecipe: function (e, t) {
            e.activeRecipe = t;
          },
        },
        getters: {
          getRenderRecipes: function (e) {
            return e.renderRecipes;
          },
          getShowRecipe: function (e) {
            return e.showRecipe;
          },
          getActiveRecipe: function (e) {
            return e.activeRecipe;
          },
          getSaveRecipe: function (e) {
            return e.saveRecipe;
          },
        },
      }),
      B = a("8c4f"),
      J = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "div",
          [
            a("h2", [e._v("Meal Plan")]),
            a("v-divider"),
            a("h2", [e._v("Recently Added")]),
            a("v-divider"),
            a("AllRecipes"),
          ],
          1
        );
      },
      H = [],
      K = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "v-row",
          e._l(e.recipes, function (t) {
            return a(
              "v-col",
              { key: t.name, attrs: { cols: "3" } },
              [
                a("v-hover", {
                  attrs: { "open-delay": 50 },
                  scopedSlots: e._u(
                    [
                      {
                        key: "default",
                        fn: function (n) {
                          var i = n.hover;
                          return [
                            a(
                              "v-card",
                              {
                                staticClass: "card-container",
                                class: { "on-hover": i },
                                attrs: { elevation: i ? 12 : 2, height: "400" },
                                on: {
                                  click: function (a) {
                                    return e.moreInfo(t.slug);
                                  },
                                },
                              },
                              [
                                a("v-img", {
                                  attrs: {
                                    height: "200",
                                    src: e.getImage(t.image),
                                  },
                                }),
                                a("v-card-title", [e._v(e._s(t.name))]),
                                a("v-card-text", [
                                  e._v(
                                    " " +
                                      e._s(
                                        e._f("truncate")(
                                          t.description,
                                          125,
                                          "..."
                                        )
                                      ) +
                                      " "
                                  ),
                                ]),
                              ],
                              1
                            ),
                          ];
                        },
                      },
                    ],
                    null,
                    !0
                  ),
                }),
              ],
              1
            );
          }),
          1
        );
      },
      q = [],
      Y = {
        data: function () {
          return { recipes: [] };
        },
        mounted: function () {
          this.getRecipes();
        },
        computed: {
          reRender: function () {
            return this.$store.getters.getRenderRecipes;
          },
        },
        watch: {
          reRender: function () {
            this.getRecipes();
          },
        },
        methods: {
          getRecipes: function () {
            var e = this;
            return Object(o["a"])(
              regeneratorRuntime.mark(function t() {
                var a, n, i;
                return regeneratorRuntime.wrap(function (t) {
                  while (1)
                    switch ((t.prev = t.next)) {
                      case 0:
                        return (
                          (a = {
                            keys: [
                              "name",
                              "slug",
                              "image",
                              "description",
                              "dateAdded",
                            ],
                          }),
                          (t.next = 3),
                          u.a.post("/api/all-recipes", a)
                        );
                      case 3:
                        (n = t.sent),
                          (i = n.data),
                          i.sort(function (e, t) {
                            return e.dateAdded > t.dateAdded ? -1 : 1;
                          }),
                          (e.recipes = i),
                          e.$store.commit("setRenderRecipes", !1);
                      case 8:
                      case "end":
                        return t.stop();
                    }
                }, t);
              })
            )();
          },
          getImage: function (e) {
            var t = "/api/recipe/image/".concat(e);
            return t;
          },
          moreInfo: function (e) {
            this.$router.push("recipe/".concat(e));
          },
        },
      },
      z = Y,
      G = a("62ad"),
      Q = a("ce87"),
      W = a("adda"),
      X = a("0fd9"),
      Z = Object(f["a"])(z, K, q, !1, null, "18bea6e4", null),
      ee = Z.exports;
    h()(Z, {
      VCard: b["a"],
      VCardText: _["b"],
      VCardTitle: _["c"],
      VCol: G["a"],
      VHover: Q["a"],
      VImg: W["a"],
      VRow: X["a"],
    });
    var te = {
        components: { AllRecipes: ee },
        mounted: function () {
          console.log("http://localhost:8000");
        },
      },
      ae = te,
      ne = Object(f["a"])(ae, J, H, !1, null, null, null),
      ie = ne.exports;
    h()(ne, { VDivider: R["a"] });
    var re = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "v-card",
          [
            a("v-img", {
              attrs: {
                "max-height": "400",
                src: e.getImage(e.recipeDetails.image),
              },
            }),
            a("v-toolbar", {
              staticClass: "card-btn",
              attrs: { flat: "", height: "0", "extension-height": "0" },
              scopedSlots: e._u([
                {
                  key: "extension",
                  fn: function () {
                    return [
                      a("v-col"),
                      e.showIcons
                        ? a(
                            "div",
                            [
                              a(
                                "v-btn",
                                {
                                  staticClass: "mr-2",
                                  attrs: {
                                    fab: "",
                                    dark: "",
                                    small: "",
                                    color: "red",
                                  },
                                  on: { click: e.deleteRecipe },
                                },
                                [a("v-icon", [e._v("mdi-delete")])],
                                1
                              ),
                              a(
                                "v-btn",
                                {
                                  staticClass: "mr-2",
                                  attrs: {
                                    fab: "",
                                    dark: "",
                                    small: "",
                                    color: "green",
                                  },
                                  on: { click: e.saveRecipe },
                                },
                                [a("v-icon", [e._v("mdi-content-save")])],
                                1
                              ),
                              a(
                                "v-btn",
                                {
                                  staticClass: "mr-5",
                                  attrs: {
                                    fab: "",
                                    dark: "",
                                    small: "",
                                    color: "secondary",
                                  },
                                  on: {
                                    click: function (t) {
                                      e.jsonEditor = !0;
                                    },
                                  },
                                },
                                [a("v-icon", [e._v("mdi-code-braces")])],
                                1
                              ),
                            ],
                            1
                          )
                        : e._e(),
                      a(
                        "v-btn",
                        {
                          attrs: {
                            color: "primary",
                            fab: "",
                            dark: "",
                            small: "",
                          },
                          on: { click: e.showForm },
                        },
                        [a("v-icon", [e._v("mdi-square-edit-outline")])],
                        1
                      ),
                    ];
                  },
                  proxy: !0,
                },
              ]),
            }),
            e.form
              ? e.showJsonEditor
                ? a("VJsoneditor", {
                    staticClass: "mt-10",
                    attrs: { height: "1500px", options: e.jsonEditorOptions },
                    model: {
                      value: e.recipeDetails,
                      callback: function (t) {
                        e.recipeDetails = t;
                      },
                      expression: "recipeDetails",
                    },
                  })
                : a("EditRecipe", {
                    model: {
                      value: e.recipeDetails,
                      callback: function (t) {
                        e.recipeDetails = t;
                      },
                      expression: "recipeDetails",
                    },
                  })
              : a("ViewRecipe", {
                  attrs: {
                    name: e.recipeDetails.name,
                    ingredients: e.recipeDetails.recipeIngredient,
                    description: e.recipeDetails.description,
                    instructions: e.recipeDetails.recipeInstructions,
                    tags: e.recipeDetails.tags,
                    categories: e.recipeDetails.categories,
                    notes: e.recipeDetails.notes,
                  },
                }),
          ],
          1
        );
      },
      se = [],
      ce = a("bcb2"),
      oe = a.n(ce),
      le = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "div",
          [
            a("v-card-title", { staticClass: "headline" }, [
              e._v(" " + e._s(e.name) + " "),
            ]),
            a(
              "v-card-text",
              [
                e._v(" " + e._s(e.description) + " "),
                a("div", { staticClass: "my-2" }),
                a(
                  "v-row",
                  [
                    a(
                      "v-col",
                      { attrs: { cols: "4" } },
                      [
                        a("h2", { staticClass: "mb-4" }, [e._v("Ingredients")]),
                        e._l(e.ingredients, function (e) {
                          return a(
                            "div",
                            { key: e },
                            [
                              a("v-checkbox", {
                                staticClass: "ingredients",
                                attrs: { "hide-details": "", label: e },
                              }),
                            ],
                            1
                          );
                        }),
                        e.categories[0]
                          ? a(
                              "div",
                              [
                                a("h2", { staticClass: "mt-4" }, [
                                  e._v("Categories"),
                                ]),
                                e._l(e.categories, function (t) {
                                  return a(
                                    "v-chip",
                                    {
                                      key: t,
                                      staticClass: "ma-1",
                                      attrs: { color: "primary", dark: "" },
                                    },
                                    [e._v(" " + e._s(t) + " ")]
                                  );
                                }),
                              ],
                              2
                            )
                          : e._e(),
                        e.tags[0]
                          ? a(
                              "div",
                              [
                                a("h2", { staticClass: "mt-4" }, [
                                  e._v("Tags"),
                                ]),
                                e._l(e.tags, function (t) {
                                  return a(
                                    "v-chip",
                                    {
                                      key: t,
                                      staticClass: "ma-1",
                                      attrs: { color: "primary", dark: "" },
                                    },
                                    [e._v(" " + e._s(t) + " ")]
                                  );
                                }),
                              ],
                              2
                            )
                          : e._e(),
                        e.notes[0]
                          ? a("h2", { staticClass: "my-4" }, [e._v("Notes")])
                          : e._e(),
                        e._l(e.notes, function (t, n) {
                          return a(
                            "v-card",
                            { key: n, staticClass: "mt-1" },
                            [
                              a("v-card-title", [e._v(" " + e._s(t.title))]),
                              a("v-card-text", [
                                e._v(" " + e._s(t.text) + " "),
                              ]),
                            ],
                            1
                          );
                        }),
                      ],
                      2
                    ),
                    a("v-divider", { attrs: { vertical: !0 } }),
                    a(
                      "v-col",
                      [
                        a("h2", { staticClass: "mb-4" }, [
                          e._v("Instructions"),
                        ]),
                        e._l(e.instructions, function (t, n) {
                          return a(
                            "div",
                            { key: t.text },
                            [
                              a("v-hover", {
                                scopedSlots: e._u(
                                  [
                                    {
                                      key: "default",
                                      fn: function (i) {
                                        var r = i.hover;
                                        return [
                                          a(
                                            "v-card",
                                            {
                                              staticClass: "ma-1",
                                              class: [
                                                { "on-hover": r },
                                                e.isDisabled(n),
                                              ],
                                              attrs: { elevation: r ? 12 : 2 },
                                              on: {
                                                click: function (t) {
                                                  return e.toggleDisabled(n);
                                                },
                                              },
                                            },
                                            [
                                              a("v-card-title", [
                                                e._v("Step: " + e._s(n + 1)),
                                              ]),
                                              a("v-card-text", [
                                                e._v(e._s(t.text)),
                                              ]),
                                            ],
                                            1
                                          ),
                                        ];
                                      },
                                    },
                                  ],
                                  null,
                                  !0
                                ),
                              }),
                            ],
                            1
                          );
                        }),
                      ],
                      2
                    ),
                  ],
                  1
                ),
              ],
              1
            ),
          ],
          1
        );
      },
      ue = [],
      de =
        (a("caad"),
        a("c975"),
        a("a434"),
        a("2532"),
        {
          props: {
            name: String,
            description: String,
            ingredients: Array,
            instructions: Array,
            categories: Array,
            tags: Array,
            notes: Array,
          },
          data: function () {
            return { disabledSteps: [] };
          },
          methods: {
            toggleDisabled: function (e) {
              if (this.disabledSteps.includes(e)) {
                var t = this.disabledSteps.indexOf(e);
                -1 !== t && this.disabledSteps.splice(t, 1);
              } else this.disabledSteps.push(e);
            },
            isDisabled: function (e) {
              return this.disabledSteps.includes(e) ? "disabled-card" : void 0;
            },
          },
        }),
      pe = de,
      ve = a("ac7c"),
      fe = a("cc20"),
      me = Object(f["a"])(pe, le, ue, !1, null, null, null),
      he = me.exports;
    h()(me, {
      VCard: b["a"],
      VCardText: _["b"],
      VCardTitle: _["c"],
      VCheckbox: ve["a"],
      VChip: fe["a"],
      VCol: G["a"],
      VDivider: R["a"],
      VHover: Q["a"],
      VRow: X["a"],
    });
    var ge = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "div",
          [
            a(
              "v-card-text",
              [
                a("v-text-field", {
                  staticClass: "my-3",
                  attrs: { label: "Recipe Name" },
                  model: {
                    value: e.value.name,
                    callback: function (t) {
                      e.$set(e.value, "name", t);
                    },
                    expression: "value.name",
                  },
                }),
                a("v-textarea", {
                  attrs: { height: "100", label: "Description" },
                  model: {
                    value: e.value.description,
                    callback: function (t) {
                      e.$set(e.value, "description", t);
                    },
                    expression: "value.description",
                  },
                }),
                a("div", { staticClass: "my-2" }),
                a(
                  "v-row",
                  [
                    a(
                      "v-col",
                      { attrs: { cols: "4" } },
                      [
                        a("h2", { staticClass: "mb-4" }, [e._v("Ingredients")]),
                        e._l(e.value.recipeIngredient, function (t, n) {
                          return a(
                            "div",
                            { key: e.generateKey("ingredient", n) },
                            [
                              a(
                                "v-row",
                                { attrs: { align: "center" } },
                                [
                                  a(
                                    "v-btn",
                                    {
                                      staticClass: "mr-2",
                                      attrs: {
                                        fab: "",
                                        "x-small": "",
                                        color: "red",
                                        elevation: "1",
                                      },
                                      on: {
                                        click: function (t) {
                                          return e.removeIngredient(n);
                                        },
                                      },
                                    },
                                    [
                                      a(
                                        "v-icon",
                                        { attrs: { color: "white" } },
                                        [e._v("mdi-delete")]
                                      ),
                                    ],
                                    1
                                  ),
                                  a("v-text-field", {
                                    attrs: { label: "Ingredient" },
                                    model: {
                                      value: e.value.recipeIngredient[n],
                                      callback: function (t) {
                                        e.$set(e.value.recipeIngredient, n, t);
                                      },
                                      expression:
                                        "value.recipeIngredient[index]",
                                    },
                                  }),
                                ],
                                1
                              ),
                            ],
                            1
                          );
                        }),
                        a(
                          "v-btn",
                          {
                            attrs: {
                              color: "primary",
                              fab: "",
                              dark: "",
                              small: "",
                            },
                            on: { click: e.addIngredient },
                          },
                          [a("v-icon", [e._v("mdi-plus")])],
                          1
                        ),
                        a("h2", { staticClass: "mt-6" }, [e._v("Categories")]),
                        a("v-combobox", {
                          attrs: {
                            dense: "",
                            multiple: "",
                            chips: "",
                            "item-color": "primary",
                            "deletable-chips": "",
                          },
                          scopedSlots: e._u([
                            {
                              key: "selection",
                              fn: function (t) {
                                return [
                                  a(
                                    "v-chip",
                                    {
                                      attrs: {
                                        "input-value": t.selected,
                                        close: "",
                                        color: "primary",
                                        dark: "",
                                      },
                                    },
                                    [e._v(" " + e._s(t.item) + " ")]
                                  ),
                                ];
                              },
                            },
                          ]),
                          model: {
                            value: e.value.categories,
                            callback: function (t) {
                              e.$set(e.value, "categories", t);
                            },
                            expression: "value.categories",
                          },
                        }),
                        a("h2", { staticClass: "mt-4" }, [e._v("Tags")]),
                        a("v-combobox", {
                          attrs: {
                            dense: "",
                            multiple: "",
                            chips: "",
                            "deletable-chips": "",
                          },
                          scopedSlots: e._u([
                            {
                              key: "selection",
                              fn: function (t) {
                                return [
                                  a(
                                    "v-chip",
                                    {
                                      attrs: {
                                        "input-value": t.selected,
                                        close: "",
                                        color: "primary",
                                        dark: "",
                                      },
                                    },
                                    [e._v(" " + e._s(t.item) + " ")]
                                  ),
                                ];
                              },
                            },
                          ]),
                          model: {
                            value: e.value.tags,
                            callback: function (t) {
                              e.$set(e.value, "tags", t);
                            },
                            expression: "value.tags",
                          },
                        }),
                        a("h2", { staticClass: "my-4" }, [e._v("Notes")]),
                        e._l(e.value.notes, function (t, n) {
                          return a(
                            "v-card",
                            {
                              key: e.generateKey("note", n),
                              staticClass: "mt-1",
                            },
                            [
                              a(
                                "v-card-text",
                                [
                                  a(
                                    "v-row",
                                    { attrs: { align: "center" } },
                                    [
                                      a(
                                        "v-btn",
                                        {
                                          staticClass: "mr-2",
                                          attrs: {
                                            fab: "",
                                            "x-small": "",
                                            color: "red",
                                            elevation: "1",
                                          },
                                          on: {
                                            click: function (t) {
                                              return e.removeNote(n);
                                            },
                                          },
                                        },
                                        [
                                          a(
                                            "v-icon",
                                            { attrs: { color: "white" } },
                                            [e._v("mdi-delete")]
                                          ),
                                        ],
                                        1
                                      ),
                                      a("v-text-field", {
                                        attrs: { label: "Title" },
                                        model: {
                                          value: e.value.notes[n]["title"],
                                          callback: function (t) {
                                            e.$set(
                                              e.value.notes[n],
                                              "title",
                                              t
                                            );
                                          },
                                          expression:
                                            "value.notes[index]['title']",
                                        },
                                      }),
                                    ],
                                    1
                                  ),
                                  a("v-textarea", {
                                    attrs: { label: "Note" },
                                    model: {
                                      value: e.value.notes[n]["text"],
                                      callback: function (t) {
                                        e.$set(e.value.notes[n], "text", t);
                                      },
                                      expression: "value.notes[index]['text']",
                                    },
                                  }),
                                ],
                                1
                              ),
                            ],
                            1
                          );
                        }),
                        a(
                          "v-btn",
                          {
                            staticClass: "mt-1",
                            attrs: {
                              color: "primary",
                              fab: "",
                              dark: "",
                              small: "",
                            },
                            on: { click: e.addNote },
                          },
                          [a("v-icon", [e._v("mdi-plus")])],
                          1
                        ),
                      ],
                      2
                    ),
                    a("v-divider", { attrs: { vertical: !0 } }),
                    a(
                      "v-col",
                      [
                        a("h2", { staticClass: "mb-4" }, [
                          e._v("Instructions"),
                        ]),
                        e._l(e.value.recipeInstructions, function (t, n) {
                          return a(
                            "div",
                            { key: n },
                            [
                              a("v-hover", {
                                scopedSlots: e._u(
                                  [
                                    {
                                      key: "default",
                                      fn: function (t) {
                                        var i = t.hover;
                                        return [
                                          a(
                                            "v-card",
                                            {
                                              staticClass: "ma-1",
                                              class: [{ "on-hover": i }],
                                              attrs: { elevation: i ? 12 : 2 },
                                            },
                                            [
                                              a(
                                                "v-card-title",
                                                [
                                                  a(
                                                    "v-btn",
                                                    {
                                                      staticClass: "mr-2",
                                                      attrs: {
                                                        fab: "",
                                                        "x-small": "",
                                                        color: "red",
                                                        elevation: "1",
                                                      },
                                                      on: {
                                                        click: function (t) {
                                                          return e.removeStep(
                                                            n
                                                          );
                                                        },
                                                      },
                                                    },
                                                    [
                                                      a(
                                                        "v-icon",
                                                        {
                                                          attrs: {
                                                            color: "white",
                                                          },
                                                        },
                                                        [e._v("mdi-delete")]
                                                      ),
                                                    ],
                                                    1
                                                  ),
                                                  e._v("Step: " + e._s(n + 1)),
                                                ],
                                                1
                                              ),
                                              a(
                                                "v-card-text",
                                                [
                                                  a("v-textarea", {
                                                    key: e.generateKey(
                                                      "instructions",
                                                      n
                                                    ),
                                                    attrs: { dense: "" },
                                                    model: {
                                                      value:
                                                        e.value
                                                          .recipeInstructions[
                                                          n
                                                        ]["text"],
                                                      callback: function (t) {
                                                        e.$set(
                                                          e.value
                                                            .recipeInstructions[
                                                            n
                                                          ],
                                                          "text",
                                                          t
                                                        );
                                                      },
                                                      expression:
                                                        "value.recipeInstructions[index]['text']",
                                                    },
                                                  }),
                                                ],
                                                1
                                              ),
                                            ],
                                            1
                                          ),
                                        ];
                                      },
                                    },
                                  ],
                                  null,
                                  !0
                                ),
                              }),
                            ],
                            1
                          );
                        }),
                        a(
                          "v-btn",
                          {
                            attrs: {
                              color: "primary",
                              fab: "",
                              dark: "",
                              small: "",
                            },
                            on: { click: e.addStep },
                          },
                          [a("v-icon", [e._v("mdi-plus")])],
                          1
                        ),
                      ],
                      2
                    ),
                  ],
                  1
                ),
              ],
              1
            ),
          ],
          1
        );
      },
      be = [],
      _e =
        (a("99af"),
        {
          props: { value: Object },
          data: function () {
            return {
              content: this.value,
              disabledSteps: [],
              description: String,
              ingredients: Array,
              instructions: Array,
              categories: Array,
              tags: Array,
            };
          },
          methods: {
            toggleDisabled: function (e) {
              if (this.disabledSteps.includes(e)) {
                var t = this.disabledSteps.indexOf(e);
                -1 !== t && this.disabledSteps.splice(t, 1);
              } else this.disabledSteps.push(e);
            },
            isDisabled: function (e) {
              return this.disabledSteps.includes(e) ? "disabled-card" : void 0;
            },
            generateKey: function (e, t) {
              var a = "".concat(e, "-").concat(t);
              return a;
            },
            deleteRecipe: function () {
              this.$emit("delete");
            },
            addIngredient: function () {
              var e = this.value.recipeIngredient;
              e.push("");
            },
            removeIngredient: function (e) {
              this.value.recipeIngredient.splice(e, 1);
            },
            addStep: function () {
              var e = this.value.recipeInstructions;
              e.push({ text: "" });
            },
            removeStep: function (e) {
              this.value.recipeInstructions.splice(e, 1);
            },
            addNote: function () {
              var e = this.value.notes;
              e.push({ text: "" });
            },
            removeNote: function (e) {
              this.value.notes.splice(e, 1);
            },
          },
        }),
      xe = _e,
      Re = (a("c619"), a("2b5d")),
      ke = a("a844"),
      Ce = Object(f["a"])(xe, ge, be, !1, null, null, null),
      Ve = Ce.exports;
    h()(Ce, {
      VBtn: g["a"],
      VCard: b["a"],
      VCardText: _["b"],
      VCardTitle: _["c"],
      VChip: fe["a"],
      VCol: G["a"],
      VCombobox: Re["a"],
      VDivider: R["a"],
      VHover: Q["a"],
      VIcon: C["a"],
      VRow: X["a"],
      VTextField: y["a"],
      VTextarea: ke["a"],
    });
    var we = "/api/recipe/",
      ye = {
        components: { VJsoneditor: oe.a, ViewRecipe: he, EditRecipe: Ve },
        data: function () {
          return {
            UrlName: this.$route.params.recipe,
            form: !1,
            jsonEditor: !1,
            jsonEditorOptions: { mode: "code", search: !1, mainMenuBar: !1 },
            recipeDetails: {
              name: "",
              description: "",
              image: "",
              recipeYield: "",
              recipeIngredient: [],
              recipeInstructions: [],
              slug: "",
              filePath: "",
              url: "",
              tags: [],
              categories: [],
              dateAdded: "",
              notes: [],
            },
          };
        },
        mounted: function () {
          this.getRecipeDetails();
        },
        computed: {
          showRecipe: function () {
            return this.$store.getters.getShowRecipe;
          },
          showIcons: function () {
            return this.form;
          },
          showJsonEditor: function () {
            return !!((!0 === this.form) & (!0 === this.jsonEditor));
          },
        },
        methods: {
          getRecipeDetails: function () {
            var e = this;
            return Object(o["a"])(
              regeneratorRuntime.mark(function t() {
                var a, n;
                return regeneratorRuntime.wrap(function (t) {
                  while (1)
                    switch ((t.prev = t.next)) {
                      case 0:
                        return (a = we + e.UrlName), (t.next = 3), u.a.get(a);
                      case 3:
                        (n = t.sent), (e.recipeDetails = n.data), (e.form = !1);
                      case 6:
                      case "end":
                        return t.stop();
                    }
                }, t);
              })
            )();
          },
          getImage: function (e) {
            if (0 != e) {
              var t = "/api/recipe/image/".concat(e);
              return t;
            }
          },
          close: function () {
            this.$store.commit("setShowRecipe", !1);
          },
          deleteRecipe: function () {
            var e = "/api/recipe/".concat(this.recipeDetails.slug, "/delete");
            u.a.delete(e), (this.form = !1), this.$router.push("/");
          },
          saveRecipe: function () {
            var e = this.recipeDetails.slug,
              t = "/api/recipe/".concat(e, "/update");
            u.a.post(t, this.recipeDetails),
              this.$store.commit("setSaveRecipe", !1),
              (this.form = !1);
          },
          showForm: function () {
            (this.form = !0), (this.jsonEditor = !1);
          },
        },
      },
      Se = ye,
      je = (a("0d48"), a("71d9")),
      Ie = Object(f["a"])(Se, re, se, !1, null, null, null),
      De = Ie.exports;
    h()(Ie, {
      VBtn: g["a"],
      VCard: b["a"],
      VCol: G["a"],
      VIcon: C["a"],
      VImg: W["a"],
      VToolbar: je["a"],
    });
    var $e = function () {
        var e = this,
          t = e.$createElement,
          a = e._self._c || t;
        return a(
          "v-card",
          [
            e.image
              ? a("v-img", { attrs: { height: "400", src: e.image } })
              : a("br"),
            a("ButtonRow", {
              on: {
                json: function (t) {
                  e.jsonEditor = !0;
                },
                editor: function (t) {
                  e.jsonEditor = !1;
                },
                save: e.createRecipe,
              },
            }),
            a(
              "v-row",
              [
                a("v-col", { attrs: { cols: "3" } }),
                a(
                  "v-col",
                  [
                    a("v-file-input", {
                      attrs: { label: "Image File", "truncate-length": "30" },
                      on: { change: e.onFileChange },
                      model: {
                        value: e.fileObject,
                        callback: function (t) {
                          e.fileObject = t;
                        },
                        expression: "fileObject",
                      },
                    }),
                  ],
                  1
                ),
                a("v-col", { attrs: { cols: "3" } }),
              ],
              1
            ),
            e.jsonEditor
              ? a("VJsoneditor", {
                  attrs: { height: "1500px", options: e.jsonEditorOptions },
                  model: {
                    value: e.recipeDetails,
                    callback: function (t) {
                      e.recipeDetails = t;
                    },
                    expression: "recipeDetails",
                  },
                })
              : a("EditRecipe", {
                  model: {
                    value: e.recipeDetails,
                    callback: function (t) {
                      e.recipeDetails = t;
                    },
                    expression: "recipeDetails",
                  },
                }),
          ],
          1
        );
      },
      Oe = [],
      Ee =
        (a("d3b7"),
        a("3ca3"),
        a("ddb0"),
        a("2b3d"),
        function () {
          var e = this,
            t = e.$createElement,
            a = e._self._c || t;
          return a("v-toolbar", {
            staticClass: "card-btn",
            attrs: { flat: "", height: "0", "extension-height": "0" },
            scopedSlots: e._u([
              {
                key: "extension",
                fn: function () {
                  return [
                    a("v-col"),
                    e.open
                      ? a(
                          "div",
                          [
                            a(
                              "v-btn",
                              {
                                staticClass: "mr-2",
                                attrs: {
                                  fab: "",
                                  dark: "",
                                  small: "",
                                  color: "red",
                                },
                                on: { click: e.deleteRecipe },
                              },
                              [a("v-icon", [e._v("mdi-delete")])],
                              1
                            ),
                            a(
                              "v-btn",
                              {
                                staticClass: "mr-2",
                                attrs: {
                                  fab: "",
                                  dark: "",
                                  small: "",
                                  color: "green",
                                },
                                on: { click: e.save },
                              },
                              [a("v-icon", [e._v("mdi-content-save")])],
                              1
                            ),
                            a(
                              "v-btn",
                              {
                                staticClass: "mr-5",
                                attrs: {
                                  fab: "",
                                  dark: "",
                                  small: "",
                                  color: "secondary",
                                },
                                on: { click: e.json },
                              },
                              [a("v-icon", [e._v("mdi-code-braces")])],
                              1
                            ),
                          ],
                          1
                        )
                      : e._e(),
                    a(
                      "v-btn",
                      {
                        attrs: {
                          color: "primary",
                          fab: "",
                          dark: "",
                          small: "",
                        },
                        on: { click: e.editor },
                      },
                      [a("v-icon", [e._v("mdi-square-edit-outline")])],
                      1
                    ),
                  ];
                },
                proxy: !0,
              },
            ]),
          });
        }),
      Ae = [],
      Te = {
        props: { open: { default: !0 } },
        methods: {
          editor: function () {
            this.$emit("editor");
          },
          save: function () {
            this.$emit("save");
          },
          deleteRecipe: function () {
            this.$emit("delete");
          },
          json: function () {
            this.$emit("json");
          },
        },
      },
      Ue = Te,
      Fe = Object(f["a"])(Ue, Ee, Ae, !1, null, null, null),
      Le = Fe.exports;
    h()(Fe, { VBtn: g["a"], VCol: G["a"], VIcon: C["a"], VToolbar: je["a"] });
    var Me = "/api/recipe/create/",
      Ne = {
        components: { VJsoneditor: oe.a, EditRecipe: Ve, ButtonRow: Le },
        data: function () {
          return {
            fileObject: null,
            image: null,
            jsonEditor: !1,
            jsonEditorOptions: { mode: "code", search: !1, mainMenuBar: !1 },
            recipeDetails: {
              name: "",
              description: "",
              image: "",
              recipeYield: "",
              recipeIngredient: [],
              recipeInstructions: [],
              slug: "",
              filePath: "",
              tags: [],
              categories: [],
              dateAdded: "",
              notes: [],
            },
          };
        },
        watch: {
          image: function () {
            console.log(this.image);
          },
        },
        methods: {
          onFileChange: function () {
            this.image = URL.createObjectURL(this.fileObject);
          },
          createRecipe: function () {
            var e = this;
            return Object(o["a"])(
              regeneratorRuntime.mark(function t() {
                var a;
                return regeneratorRuntime.wrap(function (t) {
                  while (1)
                    switch ((t.prev = t.next)) {
                      case 0:
                        return (
                          console.log(e.recipeDetails),
                          (t.next = 3),
                          u.a.post(Me, e.recipeDetails)
                        );
                      case 3:
                        (a = t.sent),
                          e.$router.push("/recipe/".concat(a.data)),
                          console.log(a);
                      case 6:
                      case "end":
                        return t.stop();
                    }
                }, t);
              })
            )();
          },
        },
      },
      Pe = Ne,
      Be = (a("eb65"), a("23a7")),
      Je = Object(f["a"])(Pe, $e, Oe, !1, null, null, null),
      He = Je.exports;
    h()(Je, {
      VCard: b["a"],
      VCol: G["a"],
      VFileInput: Be["a"],
      VImg: W["a"],
      VRow: X["a"],
    });
    var Ke = [
      { path: "/", component: ie },
      { path: "/mealie", component: ie },
      { path: "/recipe/:recipe", component: De },
      { path: "/new/", component: He },
    ];
    (n["a"].config.productionTip = !1), n["a"].use(B["a"]);
    var qe = new B["a"]({ routes: Ke, mode: "history" });
    new n["a"]({
      vuetify: M,
      store: P,
      router: qe,
      render: function (e) {
        return e(F);
      },
    }).$mount("#app");
    var Ye = function (e, t, a) {
      a = a || "...";
      var n = document.createElement("div");
      n.innerHTML = e;
      var i = n.textContent;
      return i.length > t ? i.slice(0, t) + a : i;
    };
    n["a"].filter("truncate", Ye);
  },
  "7b75": function (e, t, a) {},
  "8c85": function (e, t, a) {},
  c619: function (e, t, a) {
    "use strict";
    a("8c85");
  },
  eb65: function (e, t, a) {
    "use strict";
    a("7b75");
  },
});
//# sourceMappingURL=app.b457c0af.js.map
