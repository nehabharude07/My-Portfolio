document.addEventListener("DOMContentLoaded", function () {

    const bars = document.querySelectorAll(".bar-fill");
    const techSection = document.querySelector(".tech-section");

    if (!bars.length || !techSection) return;

    const observer = new IntersectionObserver(function (entries) {

        entries.forEach(function (entry) {

            if (entry.isIntersecting) {

                bars.forEach(function (bar) {
                    bar.style.width = bar.dataset.width;
                });

                observer.unobserve(entry.target);
            }

        });

    }, {
        threshold: 0.2
    });

    observer.observe(techSection);

});