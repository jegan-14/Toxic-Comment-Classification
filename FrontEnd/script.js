document.addEventListener("DOMContentLoaded", function () {
    let btn = document.getElementById("submitBtn");
    let outputText = document.getElementById("outputText");

    if (!btn || !outputText) {
        console.error("Button or outputText element not found!");
        return;
    }

    btn.addEventListener("click", async function () {

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

            if (data.classification === "toxic") {
                document.querySelector(".toggle").classList.add("active");
                outputText.innerText = "⚠️ This comment contains toxic content!";
            } else {
                document.querySelector(".toggle").classList.remove("active");
                outputText.innerText = "✅ This comment is safe!";
            }
        } catch (error) {
            console.error("Error:", error);
            outputText.innerText = "Error processing text!";
        }
    });
});
