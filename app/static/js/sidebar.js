document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    const mainContent = document.querySelector(".main-content");

    menuToggle.addEventListener("click", function () {
        sidebar.classList.toggle("hidden");
        mainContent.classList.toggle("expanded");
    });
});
