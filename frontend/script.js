
// VazhiKaatti Frontend JavaScript

document.addEventListener("DOMContentLoaded", function () {

    console.log("VazhiKaatti website loaded successfully!");

    // Explore Services
    const exploreButton = document.querySelector(".btn");

    if (exploreButton) {
        exploreButton.addEventListener("click", function () {
            document.querySelector("#services").scrollIntoView({
                behavior: "smooth"
            });
        });
    }

    // Navigation links
    const navLinks = document.querySelectorAll("nav a");

    navLinks.forEach(function (link) {
        link.addEventListener("click", function () {
            console.log("Navigation:", link.textContent);
        });
    });

});
