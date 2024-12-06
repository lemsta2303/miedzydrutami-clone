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
});
