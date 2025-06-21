const burgerMenu = document.getElementById('burger-menu');
const mobileNav = document.getElementById('mobile-nav');
const closeNav = document.getElementById('close-nav');
const overlay = document.getElementById('overlay');

burgerMenu.addEventListener('click', () => {
    mobileNav.classList.add('active');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
});

closeNav.addEventListener('click', closeMobileNav);
overlay.addEventListener('click', closeMobileNav);

function closeMobileNav() {
    mobileNav.classList.remove('active');
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}