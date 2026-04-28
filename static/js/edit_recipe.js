let currentStep = 1;
let ingredients = [];
let stepCount = 0;

const prepTimeMap = { minimal: 10, standard: 25, extensive: 45 };
const cookTimeMap = { minimal: 15, standard: 35, extensive: 75 };
const servingsMap = { minimal: 2,  standard: 4,  extensive: 8  };

// pre-fill ingredients from existing data
if (EXISTING_INGREDIENTS) {
    var parts = EXISTING_INGREDIENTS.split(',');
    for (var i = 0; i < parts.length; i++) {
        var trimmed = parts[i].trim();
        if (trimmed) ingredients.push(trimmed);
    }
}
drawIngredients();

// pre-fill steps from existing directions
function parseExistingSteps() {
    if (!EXISTING_DIRECTIONS) return;
    var lines = EXISTING_DIRECTIONS.split('\n');
    var currentTitle = '';
    var currentDetail = '';

    for (var i = 0; i < lines.length; i++) {
        var line = lines[i].trim();
        if (line.startsWith('Step')) {
            if (currentTitle || currentDetail) {
                addStepWithData(currentTitle, currentDetail.trim());
            }
            // extract title after "Step N: " or "Step N"
            var colonIdx = line.indexOf(':');
            currentTitle = colonIdx !== -1 ? line.slice(colonIdx + 1).trim() : '';
            currentDetail = '';
        } else if (line) {
            currentDetail += line + ' ';
        }
    }
    if (currentTitle || currentDetail) {
        addStepWithData(currentTitle, currentDetail.trim());
    }
}

function addStepWithData(title, detail) {
    stepCount++;
    var card = document.createElement('div');
    card.className = 'step-card';
    card.innerHTML =
        '<div class="step-card-header">' +
            '<span class="step-number">Step ' + stepCount + '</span>' +
            '<input type="text" class="step-title-input" placeholder="Step title..." value="' + title.replace(/"/g, '&quot;') + '">' +
            '<span class="remove-step" onclick="removeStep(this)">×</span>' +
        '</div>' +
        '<textarea class="step-detail-input" placeholder="Describe this step...">' + detail + '</textarea>';
    document.getElementById('stepsContainer').appendChild(card);
}

parseExistingSteps();
if (stepCount === 0) addStep();

// pre-fill chip selections
var selectedMealTypes = [];
var selectedDietary = [];

document.querySelectorAll('#mealTypeGroup .chip.selected').forEach(function(chip) {
    selectedMealTypes.push(chip.getAttribute('data-val'));
});
document.querySelectorAll('#dietaryGroup .chip.selected').forEach(function(chip) {
    selectedDietary.push(chip.getAttribute('data-val'));
});

// navigation
function goNext() {
    if (currentStep === 1) {
        if (!document.getElementById('recipeName').value.trim() ||
            !document.getElementById('prepTime').value ||
            !document.getElementById('cookTime').value ||
            !document.getElementById('servings').value) {
            alert('Please fill in all fields before continuing.');
            return;
        }
    }
    if (currentStep === 2) {
        var desc = document.getElementById('recipeDescription').value.trim();
        var words = desc.split(' ').filter(function(w) { return w !== ''; });
        if (words.length < 10) {
            alert('Please write a description of at least 10 words.');
            return;
        }
    }
    if (currentStep === 3) {
        if (selectedMealTypes.length === 0) { alert('Please select at least one meal type.'); return; }
        if (selectedDietary.length === 0) { alert('Please select at least one dietary option.'); return; }
    }
    currentStep++;
    document.getElementById('sliderTrack').style.transform = 'translateX(-' + ((currentStep - 1) * 20) + '%)';
    document.getElementById('stepIndicator').textContent = 'Step ' + currentStep + ' of 5';
}

function goBack() {
    currentStep--;
    document.getElementById('sliderTrack').style.transform = 'translateX(-' + ((currentStep - 1) * 20) + '%)';
    document.getElementById('stepIndicator').textContent = 'Step ' + currentStep + ' of 5';
}

// ingredients
function addIngredient() {
    var input = document.getElementById('ingredientInput');
    var val = input.value.trim();
    if (!val) return;
    ingredients.push(val);
    input.value = '';
    drawIngredients();
}

document.getElementById('ingredientInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') { e.preventDefault(); addIngredient(); }
});

function drawIngredients() {
    var list = document.getElementById('ingredientList');
    if (ingredients.length === 0) {
        list.innerHTML = "<p class='empty-hint'>No ingredients added yet</p>";
        return;
    }
    list.innerHTML = '';
    for (var i = 0; i < ingredients.length; i++) {
        var item = document.createElement('div');
        item.className = 'ingredient-item';
        item.innerHTML = ingredients[i] + ' <span class="remove-item" data-i="' + i + '">×</span>';
        list.appendChild(item);
    }
}

document.getElementById('ingredientList').addEventListener('click', function(e) {
    if (e.target.className === 'remove-item') {
        ingredients.splice(Number(e.target.getAttribute('data-i')), 1);
        drawIngredients();
    }
});

// steps
function addStep() {
    addStepWithData('', '');
}

function removeStep(el) {
    el.closest('.step-card').remove();
    stepCount = document.querySelectorAll('.step-card').length;
    document.querySelectorAll('.step-card').forEach(function(card, i) {
        card.querySelector('.step-number').textContent = 'Step ' + (i + 1);
    });
}

// photo preview
document.getElementById('recipePhoto').addEventListener('change', function() {
    var file = this.files[0];
    if (file) {
        document.getElementById('previewImg').src = URL.createObjectURL(file);
        document.getElementById('previewImg').style.display = 'block';
        document.querySelector('.upload-overlay').style.display = 'none';
        document.querySelector('.upload-card').classList.add('has-image');
    }
});

// chip toggles
document.getElementById('mealTypeGroup').addEventListener('click', function(e) {
    if (e.target.classList.contains('chip')) {
        var val = e.target.getAttribute('data-val');
        if (e.target.classList.contains('selected')) {
            e.target.classList.remove('selected');
            selectedMealTypes = selectedMealTypes.filter(function(v) { return v !== val; });
        } else {
            e.target.classList.add('selected');
            selectedMealTypes.push(val);
        }
    }
});

document.getElementById('dietaryGroup').addEventListener('click', function(e) {
    if (e.target.classList.contains('chip')) {
        var val = e.target.getAttribute('data-val');
        if (e.target.classList.contains('selected')) {
            e.target.classList.remove('selected');
            selectedDietary = selectedDietary.filter(function(v) { return v !== val; });
        } else {
            e.target.classList.add('selected');
            selectedDietary.push(val);
        }
    }
});

// save
function collectSteps() {
    var cards = document.querySelectorAll('.step-card');
    var steps = [];
    cards.forEach(function(card) {
        steps.push({
            title: card.querySelector('.step-title-input').value.trim(),
            detail: card.querySelector('.step-detail-input').value.trim()
        });
    });
    return steps;
}

function saveRecipe() {
    if (ingredients.length === 0) { alert('Please add at least one ingredient.'); return; }
    var steps = collectSteps();
    var hasContent = steps.some(function(s) { return s.detail !== ''; });
    if (!hasContent) { alert('Please describe at least one step.'); return; }

    var directions = '';
    steps.forEach(function(s, i) {
        directions += 'Step ' + (i + 1);
        if (s.title) directions += ': ' + s.title;
        directions += '\n' + s.detail + '\n\n';
    });

    var formData = new FormData();
    formData.append('recipe_name',        document.getElementById('recipeName').value.trim());
    formData.append('description',        document.getElementById('recipeDescription').value.trim());
    formData.append('prep_time',          prepTimeMap[document.getElementById('prepTime').value]);
    formData.append('cook_time',          cookTimeMap[document.getElementById('cookTime').value]);
    formData.append('servings',           servingsMap[document.getElementById('servings').value]);
    formData.append('meal_types',         selectedMealTypes.join(','));
    formData.append('dietary_preference', selectedDietary.join(','));
    formData.append('ingredients',        ingredients.join(', '));
    formData.append('directions',         directions.trim());

    var photoFile = document.getElementById('recipePhoto').files[0];
    if (photoFile) formData.append('recipe_pic', photoFile);

    fetch('/recipe/' + RECIPE_ID + '/edit', { method: 'POST', body: formData })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.success) {
            window.location.href = '/recipe/' + RECIPE_ID;
        } else {
            alert('Error saving: ' + (data.error || 'Unknown error'));
        }
    });
}