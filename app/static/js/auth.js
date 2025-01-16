document.addEventListener("DOMContentLoaded", function() {
    // Auto-hide flash messages after 3 seconds
    setTimeout(() => {
        let flashMessages = document.querySelectorAll('.alert');
        flashMessages.forEach(msg => {
            msg.style.transition = "opacity 0.5s";
            msg.style.opacity = "0";
            setTimeout(() => msg.remove(), 500);
        });
    }, 3000);
});
