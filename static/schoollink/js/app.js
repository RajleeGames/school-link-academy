document.addEventListener("DOMContentLoaded", function() {
    const sidebar = document.querySelector(".sl-sidebar");
    const toggleBtn = document.querySelector("[data-sidebar-toggle]");
    const closeBtns = document.querySelectorAll("[data-sidebar-close]");
    const menuGroups = document.querySelectorAll(".sl-menu-group");

    const themeToggle = document.querySelector("[data-theme-toggle]");
    const themeIcon = document.querySelector(".sl-theme-icon");
    const themeText = document.querySelector(".sl-theme-text");

    const COLLAPSED_KEY = "schoolLinkSidebarCollapsed";
    const THEME_KEY = "schoolLinkTheme";

    function isMobile() {
        return window.innerWidth < 992;
    }

    function openSidebar() {
        if (!sidebar) return;

        sidebar.classList.add("show");
        document.body.classList.add("sidebar-open");
    }

    function closeSidebar() {
        if (!sidebar) return;

        sidebar.classList.remove("show");
        document.body.classList.remove("sidebar-open");
    }

    function applySavedDesktopState() {
        if (isMobile()) {
            document.body.classList.remove("sidebar-collapsed");
            return;
        }

        const saved = localStorage.getItem(COLLAPSED_KEY);

        if (saved === "yes") {
            document.body.classList.add("sidebar-collapsed");
        } else {
            document.body.classList.remove("sidebar-collapsed");
        }
    }

    function applyTheme(theme) {
        if (theme === "dark") {
            document.documentElement.setAttribute("data-theme", "dark");

            if (themeIcon) {
                themeIcon.textContent = "☀️";
            }

            if (themeText) {
                themeText.textContent = "Light";
            }
        } else {
            document.documentElement.setAttribute("data-theme", "light");

            if (themeIcon) {
                themeIcon.textContent = "🌙";
            }

            if (themeText) {
                themeText.textContent = "Dark";
            }
        }
    }

    function loadTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY);

        if (savedTheme === "dark") {
            applyTheme("dark");
        } else {
            applyTheme("light");
        }
    }

    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute("data-theme");

        if (currentTheme === "dark") {
            localStorage.setItem(THEME_KEY, "light");
            applyTheme("light");
        } else {
            localStorage.setItem(THEME_KEY, "dark");
            applyTheme("dark");
        }
    }

    function keepActiveMenuVisible() {
        const activeLink = document.querySelector(
            ".sl-sidebar .sl-submenu-link.active, .sl-sidebar .sl-menu-link.active"
        );

        if (!activeLink || !sidebar || isMobile()) return;

        setTimeout(function() {
            const top = activeLink.offsetTop - 120;

            sidebar.scrollTo({
                top: top > 0 ? top : 0,
                behavior: "smooth"
            });
        }, 150);
    }

    function closeOtherMenus(currentGroup) {
        menuGroups.forEach(function(otherGroup) {
            if (otherGroup !== currentGroup) {
                otherGroup.classList.remove("open");
            }
        });
    }

    loadTheme();
    applySavedDesktopState();
    keepActiveMenuVisible();

    if (themeToggle) {
        themeToggle.addEventListener("click", function(event) {
            event.preventDefault();
            toggleTheme();
        });
    }

    if (toggleBtn) {
        toggleBtn.addEventListener("click", function() {
            if (isMobile()) {
                if (sidebar && sidebar.classList.contains("show")) {
                    closeSidebar();
                } else {
                    openSidebar();
                }

                return;
            }

            document.body.classList.toggle("sidebar-collapsed");

            if (document.body.classList.contains("sidebar-collapsed")) {
                localStorage.setItem(COLLAPSED_KEY, "yes");
            } else {
                localStorage.setItem(COLLAPSED_KEY, "no");
            }
        });
    }

    closeBtns.forEach(function(btn) {
        btn.addEventListener("click", closeSidebar);
    });

    menuGroups.forEach(function(group) {
        const toggle = group.querySelector(".sl-menu-toggle");

        if (!toggle) return;

        toggle.addEventListener("click", function() {
            if (!isMobile() && document.body.classList.contains("sidebar-collapsed")) {
                document.body.classList.remove("sidebar-collapsed");
                localStorage.setItem(COLLAPSED_KEY, "no");
            }

            const isOpen = group.classList.contains("open");

            closeOtherMenus(group);

            if (isOpen) {
                group.classList.remove("open");
            } else {
                group.classList.add("open");

                setTimeout(function() {
                    if (!sidebar) return;

                    const groupTop = group.offsetTop - 90;

                    sidebar.scrollTo({
                        top: groupTop > 0 ? groupTop : 0,
                        behavior: "smooth"
                    });
                }, 80);
            }
        });
    });

    document.querySelectorAll(".sl-sidebar a").forEach(function(link) {
        link.addEventListener("click", function() {
            if (isMobile()) {
                closeSidebar();
            }
        });
    });

    document.addEventListener("keydown", function(event) {
        if (event.key === "Escape") {
            closeSidebar();
        }
    });

    window.addEventListener("resize", function() {
        closeSidebar();
        applySavedDesktopState();
    });
});