document.addEventListener('DOMContentLoaded', () => {
    const searchWidget = document.querySelector('#search_widget');
    const searchLoop = document.querySelector('.material-icons.search');

    if (searchLoop) {
        searchLoop.addEventListener('click', () => {
            searchWidget.classList.toggle('active');
        });
    }
});
