const posts = document.querySelectorAll('.meal-post');
const modal = document.getElementById('meal-modal');
const backdrop = document.getElementById('modal-backdrop');

posts.forEach(function(post) {
    post.addEventListener('click', function() {
        document.getElementById('modal-image').src = post.dataset.image;
        document.getElementById('modal-title').textContent = post.dataset.title;
        document.getElementById('modal-description').textContent = post.dataset.description || '';

// badges — replace the existing badges section
var badges = document.getElementById('modal-badges');
badges.innerHTML = '';
if (post.dataset.prep) {
    var prepVal = parseInt(post.dataset.prep);
    var prepColor = prepVal <= 10 ? '#4a90d9' : prepVal <= 25 ? '#8b5cf6' : '#e05555';
    badges.innerHTML += '<span style="background:' + prepColor + ';color:white;padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Prep ' + post.dataset.prep + ' min</span>';
}
if (post.dataset.cook) {
    var cookVal = parseInt(post.dataset.cook);
    var cookColor = cookVal <= 15 ? '#4a90d9' : cookVal <= 35 ? '#8b5cf6' : '#e05555';
    badges.innerHTML += '<span style="background:' + cookColor + ';color:white;padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Cook ' + post.dataset.cook + ' min</span>';
}
if (post.dataset.servings) {
    var servVal = parseInt(post.dataset.servings);
    var servColor = servVal <= 2 ? '#4a90d9' : servVal <= 6 ? '#8b5cf6' : '#e05555';
    badges.innerHTML += '<span style="background:' + servColor + ';color:white;padding:6px 16px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Serves ' + post.dataset.servings + '</span>';
}

        // meal type tags
        var tagsDiv = document.getElementById('modal-tags');
        tagsDiv.innerHTML = '';
        if (post.dataset.mealType) {
            post.dataset.mealType.split(',').forEach(function(tag) {
                var t = tag.trim();
                if (t) tagsDiv.innerHTML += '<span style="background:#fff3e0;color:#e07b00;border:1px solid #ffd08a;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;">' + t + '</span>';
            });
        }

        // ingredients
        var ingDiv = document.getElementById('modal-ingredients');
        ingDiv.innerHTML = '';
        if (post.dataset.ingredients) {
            var items = post.dataset.ingredients.split(',');
            var html = '<p style="font-size:10px;font-weight:700;color:#999;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;">Ingredients</p>';
            html += '<div style="display:flex;flex-wrap:wrap;gap:4px;">';
            items.forEach(function(item) {
                var t = item.trim();
                if (t) html += '<span style="background:#f0f0f0;color:#555;padding:3px 10px;border-radius:20px;font-size:12px;">' + t + '</span>';
            });
            html += '</div>';
            ingDiv.innerHTML = html;
        }

        document.getElementById('view-recipe-btn').href = '/recipe/' + post.dataset.id;
        document.getElementById('edit-recipe-btn').href = '/recipe/' + post.dataset.id + '/edit';
        document.getElementById('delete-recipe-btn').setAttribute('data-id', post.dataset.id);

        modal.style.display = 'block';
        backdrop.style.display = 'block';
    });
});


document.getElementById('close-modal').addEventListener('click', closeModal);
document.getElementById('modal-backdrop').addEventListener('click', closeModal);

function closeModal() {
    modal.style.display = 'none';
    backdrop.style.display = 'none';
}

document.getElementById('delete-recipe-btn').addEventListener('click', function() {
    var id = this.getAttribute('data-id');
    if (!confirm('Delete this recipe?')) return;
    fetch('/recipe/' + id + '/delete', { method: 'POST' })
    .then(function(r) { return r.json(); })
    .then(function(data) {
        if (data.success) window.location.reload();
        else alert(data.error || 'Could not delete.');
    });
});