// plays video slideshow for landing page hero section

  var video1 = document.getElementById('video1');
  video1.playbackRate = 0.8;   // slows down shorter videos
  var video2 = document.getElementById('video2');
  video2.playbackRate = 0.8;
  var video3 = document.getElementById('video3');
  video3.playbackRate = 0.65;
  var video4 = document.getElementById('video4');

  // when one video ends, play the next
  video1.onended = function() {
    video2.style.zIndex = 10;
    video1.style.zIndex = 1;
    video2.play();
    video1.style.opacity = 0;
    video2.style.opacity = 1;
  }
  video2.onended = function() {
    video3.style.zIndex = 10;
    video2.style.zIndex = 1;
    video3.play();
    video2.style.opacity = 0;
    video3.style.opacity = 1;
  }
  video3.onended = function() {
    video4.style.zIndex = 10;
    video3.style.zIndex = 1;
    video4.play();
    video3.style.opacity = 0;
    video4.style.opacity = 1;
  }
  video4.onended = function() {
    video4.style.opacity = 0;
    video1.style.zIndex = 10;
    video4.style.zIndex = 1;
    video1.play();
    video1.style.opacity = 1;
  }
  
  video1.oncanplay = function() {
    video1.play();
  };