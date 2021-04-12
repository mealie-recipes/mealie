export const recipeIngredient = function(quantity, unit) {
  this.quantity = quantity;
  this.unit = unit;
};

recipeIngredient.prototype.isSingular = function() {
  return this.quantity > 0 && this.quantity <= 1;
};

recipeIngredient.prototype.pluralize = function() {
  if (this.isSingular()) {
    return this.unit;
  } else {
    return `${this.unit}s`;
  }
};

recipeIngredient.prototype.getSingularUnit = function() {
  if (this.isSingular()) {
    return this.unit;
  } else {
    return this.unit.replace(/s$/, "");
  }
};

recipeIngredient.prototype.toString = function() {
  return `${this.quantity.toString()} ${this.pluralize()}`;
};

recipeIngredient.prototype.convertUnits = function() {
  const conversion = recipeIngredient.CONVERSIONS[this.unit] || {};
  if (conversion.min && this.quantity < conversion.min.value) {
    this.unit = conversion.min.next;
    this.quantity.multiply(conversion.to[this.unit]);
  } else if (conversion.max && this.quantity >= conversion.max.value) {
    this.unit = conversion.max.next;
    this.quantity.multiply(conversion.to[this.unit]);
  }
  return this;
};

recipeIngredient.CONVERSIONS = {
  cup: {
    to: {
      tablespoon: 16,
    },
    min: {
      value: 1 / 4,
      next: "tablespoon",
    },
  },
  tablespoon: {
    to: {
      teaspoon: 3,
      cup: 1 / 16,
    },
    min: {
      value: 1,
      next: "teaspoon",
    },
    max: {
      value: 4,
      next: "cup",
    },
  },
  teaspoon: {
    to: {
      tablespoon: 1 / 3,
    },
    max: {
      value: 3,
      next: "tablespoon",
    },
  },
};
