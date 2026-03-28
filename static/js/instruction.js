// js for recipe instructions page

document.getElementById("instructionsForm").addEventListener("submit", function(e) {
    e.preventDefault();
    console.log("Prep time:", document.getElementById("prepMins").value + " min");
    console.log("Cook time:", document.getElementById("cookMins").value + " min");
    console.log("Servings:", document.getElementById("servings").value);
    console.log("Ingredients:", document.getElementById("ingredients").value);
    console.log("Steps:", document.getElementById("steps").value);
    console.log("Notes:", document.getElementById("recipeNotes").value);
});