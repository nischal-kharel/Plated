// filter panel toggles
const toggles = document.querySelectorAll(".filter-toggle");
for (let i = 0; i < toggles.length; i++) {
    toggles[i].addEventListener("click", function () {
        this.parentElement.classList.toggle("open");
    });
}

function getFilters() {
    const params = new URLSearchParams();

    document.querySelectorAll('.dietary-cb:checked').forEach(function(cb) {
        params.append('dietary', cb.value);
    });

    const cookChecked = Array.from(document.querySelectorAll('.cooktime-cb:checked'))
        .map(function(cb) { return parseInt(cb.value); });
    if (cookChecked.length > 0) {
        params.append('cook_time', Math.max.apply(null, cookChecked));
    }

    document.querySelectorAll('.mealtype-cb:checked').forEach(function(cb) {
        params.append('meal_type', cb.value);
    });

    const ratingChecked = Array.from(document.querySelectorAll('.rating-cb:checked'))
        .map(function(cb) { return parseFloat(cb.value); });
    if (ratingChecked.length > 0) {
        params.append('rating', Math.min.apply(null, ratingChecked));
    }

    return params;
}

function renderRecipes(recipes) {
    const grid = document.getElementById('results-grid');
    const noResults = document.getElementById('no-results');

    grid.innerHTML = '';

    if (recipes.length === 0) {
        noResults.style.display = 'block';
        return;
    }

    noResults.style.display = 'none';

    for (let i = 0; i < recipes.length; i++) {
        const r = recipes[i];
        const card = document.createElement('a');
        card.href = '/recipe/' + r.recipe_id;
        card.className = 'recipe-card';

        if (r.recipe_pic) {
            card.innerHTML = '<img src="/static/' + r.recipe_pic + '" alt="' + r.recipe_name + '">';
        } else {
            card.innerHTML = '<div class="recipe-card-name">' + r.recipe_name + '</div>';
        }

        grid.appendChild(card);
    }
}

function fetchRecipes() {
    fetch('/search/results?' + getFilters().toString())
        .then(function(res) { return res.json(); })
        .then(function(data) { renderRecipes(data.recipes); });
}

document.querySelectorAll('.filter-options input[type="checkbox"]').forEach(function(cb) {
    cb.addEventListener('change', fetchRecipes);
});

fetchRecipes();
