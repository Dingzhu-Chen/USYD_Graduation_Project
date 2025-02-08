const viewDetailsBtns = document.querySelectorAll('.view-details-btn');
const modalImage = document.getElementById('modal-image');

viewDetailsBtns.forEach(btn => {
    btn.addEventListener('click', function () {
        const imgSrc = this.getAttribute('data-img-src');
        modalImage.src = imgSrc;
    });
});
