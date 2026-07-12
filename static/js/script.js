/**
 * script.js
 * ---------
 * Small front-end enhancements shared across every page.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Auto-dismiss flash messages after 4 seconds
    document.querySelectorAll(".alert").forEach((alertEl) => {
        setTimeout(() => {
            const alert = bootstrap.Alert.getOrCreateInstance(alertEl);
            alert.close();
        }, 4000);
    });
});
