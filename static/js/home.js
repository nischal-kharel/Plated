// js for home page

// trending recipes
fetch("/get_recipes")
    .then(function(res) { return res.json(); })
    .then(function(data) {
        let carousel = document.getElementById("topRecipesCarousel");
        carousel.innerHTML = "";
        for (let i = 0; i < data.recipes.length; i++) {
            let recipe = data.recipes[i];
            let a = document.createElement("a");
            a.href = "/recipe/" + recipe.recipe_id;
            if (recipe.recipe_pic) {
                let img = document.createElement("img");
                img.src = "/static/" + recipe.recipe_pic;
                img.alt = recipe.recipe_name;
                a.appendChild(img);
            }
            carousel.appendChild(a);
        }
    });

// friend activity
fetch("/get_feed_recipes")
    .then(function(res) { return res.json(); })
    .then(function(data) {
        let carousel = document.getElementById("friendActivityCarousel");
        carousel.innerHTML = "";
        if (data.recipes.length === 0) {
            carousel.innerHTML = "<p>No activity yet. Follow some users!</p>";
            return;
        }
        for (let i = 0; i < data.recipes.length; i++) {
            let recipe = data.recipes[i];
            let a = document.createElement("a");
            a.href = "/recipe/" + recipe.recipe_id;
            if (recipe.recipe_pic) {
                let img = document.createElement("img");
                img.src = "/static/" + recipe.recipe_pic;
                img.alt = recipe.recipe_name;
                a.appendChild(img);
            }
            carousel.appendChild(a);
        }
    });