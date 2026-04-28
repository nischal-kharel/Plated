function buildRecipeCard(recipe) {
  let a = document.createElement("a");
  a.href = "/recipe/" + recipe.recipe_id;
  a.className = "carousel-card";

  let img = document.createElement("img");
  img.className = "card-img";
  img.src = recipe.recipe_pic ? "/static/" + recipe.recipe_pic : "/static/img/placeholder.png";
  img.alt = recipe.recipe_name || "Recipe";
  a.appendChild(img);

  let meta = document.createElement("div");
  meta.className = "carousel-card-meta";
  meta.textContent = recipe.recipe_name || "";
  a.appendChild(meta);

  return a;
}

function buildFriendCard(item) {
  let a = document.createElement("a");
  // route to recipe or journal depending on type
  a.href = item.item_type === 'meal' ? "/journal" : "/recipe/" + item.item_id;
  a.className = "carousel-card";

  let img = document.createElement("img");
  img.className = "card-img";
  img.src = item.item_pic ? "/static/" + item.item_pic : "/static/img/placeholder.png";
  img.alt = item.item_name || "";
  a.appendChild(img);

  let meta = document.createElement("div");
  meta.className = "carousel-card-meta";
  meta.textContent = item.item_name || "";
  a.appendChild(meta);

  let userRow = document.createElement("div");
  userRow.className = "carousel-card-user";

  let pfp = document.createElement("img");
  pfp.className = "carousel-card-pfp";
pfp.src = item.profile_pic
    ? "/static/" + item.profile_pic
    : "/static/media/profileimages/default-pfp.svg";
  pfp.alt = item.username || "";
  userRow.appendChild(pfp);

  let uname = document.createElement("span");
  uname.className = "carousel-card-username";
  uname.textContent = item.username || "";
  userRow.appendChild(uname);

  a.appendChild(userRow);
  return a;
}

// ── Trending Recipes ──
fetch("/get_recipes").then(r => r.json()).then(function(data) {
  let carousel = document.getElementById("topRecipesCarousel");
  if (!carousel) return;
  carousel.innerHTML = "";
  let recipes = data.recipes || [];
  carousel.style.setProperty("--items", recipes.length);
  recipes.forEach(function(recipe) {
    carousel.appendChild(buildRecipeCard(recipe));
  });
});

// ── Friend Activity ──
fetch("/get_feed_recipes").then(r => r.json()).then(function(data) {
  let carousel = document.getElementById("friendActivityCarousel");
  if (!carousel) return;
  let items = data.recipes || [];
  carousel.style.setProperty("--items", items.length);
  items.forEach(function(item) {
    carousel.appendChild(buildFriendCard(item));
  });
});