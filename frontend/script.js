
document.addEventListener("DOMContentLoaded", function () {

    // Load services from Flask + SQLite
    async function loadServices() {

        try {
            const response = await fetch("/api/services");

            if (!response.ok) {
                throw new Error("Services could not be loaded");
            }

            const data = await response.json();

            console.log("VazhiKaatti services loaded:", data.services);

            const serviceGrid =
                document.querySelector(".service-grid");

            if (!serviceGrid) return;

            const serviceLinks = {
                "Local Services": "local-services.html",
                "Community Updates": "community.html",
                "Report Issues": "complaints.html",
                "Connect People": "connect.html"
            };

            const serviceIcons = {
                "Local Services": "🏛️",
                "Community Updates": "📢",
                "Report Issues": "⚠️",
                "Connect People": "👥"
            };

            const serviceClasses = {
                "Local Services": "local",
                "Community Updates": "community",
                "Report Issues": "complaints",
                "Connect People": "connect"
            };

            serviceGrid.innerHTML = "";

            data.services.forEach(function (service) {

                const card = document.createElement("a");

                card.className =
                    "service-card " +
                    (serviceClasses[service.service_name] || "local");

                card.href =
                    serviceLinks[service.service_name] || "#";

                const icon = document.createElement("div");
                icon.className = "service-icon";
                icon.textContent =
                    serviceIcons[service.service_name] || "🌱";

                const title = document.createElement("h3");
                title.textContent = service.service_name;

                const description = document.createElement("p");
                description.textContent = service.description;

                const button = document.createElement("span");
                button.textContent = "Explore →";

                card.appendChild(icon);
                card.appendChild(title);
                card.appendChild(description);
                card.appendChild(button);

                serviceGrid.appendChild(card);

            });

        } catch (error) {
            console.error("VazhiKaatti error:", error);
        }
    }

    loadServices();

});
