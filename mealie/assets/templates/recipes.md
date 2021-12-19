

![Recipe Image](../../images/{{ recipe.slug }}/original.jpg)

# {{ recipe.name }}
{{ recipe.description }}

## Ingredients
{% for ingredient in recipe.recipeIngredient %} 
- [ ] {{ ingredient }} {% endfor %}

## Instructions
{% for step in recipe.recipeInstructions %} 
- [ ] {{ step.text }} {% endfor %}

{% for note in recipe.notes %}
**{{ note.title }}:** {{ note.text }}
{% endfor %}

---

Tags: {{ recipe.tags }}
Categories: {{ recipe.categories }}
Original URL: {{ recipe.orgURL }}