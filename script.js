// Interactive replay: the viewer (and its ~28 MB of assets) loads only on click.
document.getElementById('launch').addEventListener('click', () => {
  const frame = document.getElementById('replay-frame');
  const f = document.createElement('iframe');
  f.src = './replay/index.html?speed=4';
  f.title = 'Interactive replay of the factory line';
  f.allow = 'fullscreen';
  frame.replaceChildren(f);
});

// highlight the nav pill for the section in view
const links = [...document.querySelectorAll('.pill a')];
const io = new IntersectionObserver((es) => {
  es.forEach((e) => {
    if (e.isIntersecting) links.forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
  });
}, { rootMargin: '-45% 0px -50% 0px' });
links.forEach((a) => io.observe(document.querySelector(a.getAttribute('href'))));
