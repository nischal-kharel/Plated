const FULL = "/static/media/ratingimages/fullplate.png";
const HALF = "/static/media/ratingimages/leftbrokenplate.png";

// Draw star ratings on each card
document.querySelectorAll('.review-card-score').forEach(function(el) {
    const score = parseFloat(el.getAttribute('data-score'));
    let html = '';
    for (let i = 1; i <= 5; i++) {
        if (score >= i)          html += '<img src="' + FULL + '">';
        else if (score >= i-0.5) html += '<img src="' + HALF + '">';
        else                     html += '<img src="' + FULL + '" style="opacity:0.2">';
    }
    el.innerHTML = html;
});

// Like buttons
document.querySelectorAll('.review-card-like').forEach(function(btn) {
    btn.addEventListener('click', function() {
        const reviewId = this.getAttribute('data-review-id');
        const liked = this.getAttribute('data-liked') === 'true';
        const count = parseInt(this.getAttribute('data-count'));

        fetch('/review/' + reviewId + '/like', { method: 'POST' })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                const newLiked = data.liked;
                const newCount = newLiked ? count + 1 : count - 1;
                btn.setAttribute('data-liked', newLiked);
                btn.setAttribute('data-count', newCount);
                btn.classList.toggle('liked', newLiked);
                btn.textContent = (newLiked ? '♥ ' : '♡ ') + newCount + (newCount === 1 ? ' like' : ' likes');
            }
        });
    });
});

document.querySelectorAll('.review-card-delete').forEach(function(btn) {
    btn.addEventListener('click', function() {
        if (!confirm('Delete this review?')) return;
        const reviewId = this.getAttribute('data-review-id');
        fetch('/review/' + reviewId + '/delete', { method: 'POST' })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            if (data.success) {
                btn.closest('.review-card').remove();
            } else {
                alert(data.error || 'Could not delete review.');
            }
        });
    });
});