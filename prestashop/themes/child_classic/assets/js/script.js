document.addEventListener('DOMContentLoaded', () => {
    const searchWidget = document.querySelector('#search_widget');
    const searchLoop = document.querySelector('.material-icons.search');

    if (searchLoop) {
        searchLoop.addEventListener('click', () => {
            searchWidget.classList.toggle('active');
        });
    }

    const tabs = document.querySelectorAll('.tabs-list li');
    const sections = document.querySelectorAll('.category-section');

    if (tabs.length > 0 && sections.length > 0) {
        tabs[0].classList.add('active'); // Pierwszy tab
        sections[0].style.display = 'flex';
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', function () {
            const target = tab.getAttribute('data-tab');

            tabs.forEach(t => t.classList.remove('active'));
            sections.forEach(section => {
                section.style.display = 'none';
            });

            document.getElementById(target).style.display = 'flex';
            tab.classList.add('active');
        });
    });

    const productImages = document.querySelectorAll('.product-carousel img'); // Wszystkie obrazy w karuzeli
    const largeImage = document.getElementById('large-product-image'); // Duże zdjęcie
    const leftArrow = document.querySelector('.carousel-arrow.left'); // Strzałka lewa
    const rightArrow = document.querySelector('.carousel-arrow.right'); // Strzałka prawa
    const products = document.querySelectorAll('.product-carousel .product'); // Produkty w karuzeli
    let currentIndex = 0;

    const updateActiveProduct = () => {
        products.forEach((product, index) => {
            product.style.display = index === currentIndex ? 'block' : 'none';
        });
        if(productImages[currentIndex].dataset){
            largeImage.src = productImages[currentIndex].dataset.large || productImages[currentIndex].src;
        }
    };

    if(leftArrow){
        leftArrow.addEventListener('click', () => {
            currentIndex = (currentIndex - 1 + products.length) % products.length;
            updateActiveProduct();
        });
    }
    if(rightArrow){
        rightArrow.addEventListener('click', () => {
            currentIndex = (currentIndex + 1) % products.length;
            updateActiveProduct();
        });
    }
    updateActiveProduct();
});
