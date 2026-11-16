
document.addEventListener("DOMContentLoaded", function () {

    const serviceList = document.getElementById("service-list");
    const message = document.getElementById("service-message");

    async function loadServices() {
        try {
            const response = await fetch("/api/services");

            if (!response.ok) {
                throw new Error("Unable to load services");
            }

            const data = await response.json();

            serviceList.innerHTML = "";

            data.services.forEach(function (service) {
                const card = document.createElement("div");
                card.className = "service-card";

                const title = document.createElement("h3");
                title.textContent = service.service_name;

                const description = document.createElement("p");
                description.textContent = service.description;

                card.appendChild(title);
                card.appendChild(description);
                serviceList.appendChild(card);
            });

            message.textContent = "Our available services";

        } catch (error) {
            message.textContent = "Services could not be loaded. Please try again.";
            console.error(error);
        }
    }

    loadServices();

});
