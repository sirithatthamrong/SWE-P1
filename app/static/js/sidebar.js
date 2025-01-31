document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.querySelector(".main-content");

    menuToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
        mainContent.classList.toggle("expanded");
    });
});

document.addEventListener("DOMContentLoaded", function () {
    let currentPath = window.location.pathname;

    document.querySelectorAll(".sidebar .nav a").forEach(link => {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("active");
        }
    });
});
