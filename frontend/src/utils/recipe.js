export const recipe = {
  /**
   * Sorts a list of recipes in place
   * @param {Array<Object>} list of recipes
   * @param {Boolean} inverse - Z or A First
   */
  sortAToZ(list) {
    list.sort((a, b) => {
      var textA = a.name.toUpperCase();
      var textB = b.name.toUpperCase();
      return textA < textB ? -1 : textA > textB ? 1 : 0;
    });
  },
  sortByCreated(list) {
    list.sort((a, b) => (a.dateAdded > b.dateAdded ? -1 : 1));
  },
  sortUpdated(list) {
    list.sort((a, b) => (a.dateUpdated > b.dateUpdated ? -1 : 1));
  },
  sortByRating(list) {
    list.sort((a, b) => (a.rating > b.rating ? -1 : 1));
  },
  /**
   *
   * @param {Array<Object>} list
   * @returns String / Recipe Slug
   */
  randomRecipe(list) {
    return list[Math.floor(Math.random() * list.length)];
  },
};
