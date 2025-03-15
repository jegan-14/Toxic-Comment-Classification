document.addEventListener("DOMContentLoaded", function () {
    let toggle = document.querySelector(".toggle");
    document.getElementById("submitBtn").addEventListener("click", async function () {
        let inputText = document.getElementById("commentInput").value.trim();
        if (!inputText) {
            alert("Please enter a comment.");
            return;
        }

        try {
            let response = await fetch("http://127.0.0.1:5000/classify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: inputText })
            });

            let data = await response.json();
            
            let outputContainer = document.getElementById("outputContainer");
            outputContainer.innerHTML = ""; // Clear previous results


            if (data.classification === "safe comment") {
                // Show safe message
                toggle.classList.remove("active");
                let safeText = document.createElement("p");
                safeText.innerText = `✅ Safe Comment`;
                safeText.style.color = "green";
                outputContainer.appendChild(safeText);
            } else {
                // Show toxic message
                toggle.classList.add("active");
                let toxicText = document.createElement("p");
                toxicText.innerText = `⚠️ Toxic Comment`;
                toxicText.style.color = "red";
                outputContainer.appendChild(toxicText);

                // Show filtered text
                let filteredText = document.createElement("p");
                filteredText.innerText = `🚫 Filtered: ${data.filtered_text}`;
                filteredText.style.color = "blue";
                outputContainer.appendChild(filteredText);
            }
        } catch (error) {
            console.error("Error:", error);
            document.getElementById("outputContainer").innerText = "Error processing text!";
        }
    });
});
