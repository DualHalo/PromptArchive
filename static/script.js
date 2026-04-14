const form = document.getElementById("promptForm");
const generatedPrompt = document.getElementById("generatedPrompt");
const copyBtn = document.getElementById("copyBtn");
const surpriseBtn = document.getElementById("surpriseBtn");
const copiedPill = document.getElementById("copiedPill");

const surpriseSets = {
    subject: [
        "confident fashion model",
        "mysterious fantasy heroine",
        "luxury lifestyle influencer",
        "elegant businesswoman",
        "cinematic sci-fi protagonist"
    ],
    lighting: [
        "soft natural lighting",
        "moody cinematic lighting",
        "glowing golden hour lighting",
        "dramatic studio lighting",
        "soft diffused window light"
    ],
    camera: [
        "85mm portrait lens",
        "50mm prime lens",
        "iPhone photo look",
        "cinematic anamorphic lens",
        "high-end fashion editorial camera setup"
    ],
    environment: [
        "lush botanical garden",
        "luxury rooftop terrace",
        "modern apartment interior",
        "sunlit beach boardwalk",
        "moody candlelit lounge"
    ],
    time_of_day: [
        "morning",
        "afternoon",
        "golden hour",
        "sunset",
        "night"
    ],
    hair_length: [
        "short",
        "medium-length",
        "long"
    ],
    hair_style: [
        "sleek straight",
        "soft wavy",
        "loose curls",
        "messy bun",
        "side-swept layers",
        "romantic updo"
    ],
    hair_color: [
        "dark brown with soft highlights",
        "platinum blonde",
        "jet black",
        "warm auburn",
        "chestnut brown"
    ],
    outfit_type: [
        "dress",
        "blazer ensemble",
        "gown",
        "casual outfit",
        "streetwear look"
    ],
    outfit_style: [
        "elegant",
        "glamorous",
        "editorial",
        "tailored",
        "cozy"
    ],
    outfit_color: [
        "black",
        "blush pink",
        "ivory",
        "emerald green",
        "deep navy"
    ]
};

function randomItem(items) {
    return items[Math.floor(Math.random() * items.length)];
}

async function refreshPrompt() {
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    generatedPrompt.value = data.prompt;
}

function flashCopied() {
    copiedPill.classList.add("show");
    window.setTimeout(() => copiedPill.classList.remove("show"), 1200);
}

form.addEventListener("input", refreshPrompt);
form.addEventListener("change", refreshPrompt);

copyBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(generatedPrompt.value);
    flashCopied();
});

surpriseBtn.addEventListener("click", async () => {
    Object.entries(surpriseSets).forEach(([fieldName, values]) => {
        const field = form.elements.namedItem(fieldName);
        if (field) {
            field.value = randomItem(values);
        }
    });

    await refreshPrompt();
});

document.querySelectorAll(".favorite-toggle").forEach((button) => {
    button.addEventListener("click", async () => {
        const promptId = button.dataset.id;
        const response = await fetch(`/favorite/${promptId}`, {
            method: "POST"
        });

        const data = await response.json();
        if (data.ok) {
            button.textContent = data.is_favorite ? "⭐" : "☆";
            window.location.reload();
        }
    });
});

document.querySelectorAll(".load-btn").forEach((button) => {
    button.addEventListener("click", async () => {
        const promptId = button.dataset.id;
        const response = await fetch(`/load/${promptId}`);
        const data = await response.json();

        if (!data.ok) return;

        const prompt = data.prompt;

        const mappings = [
            "title",
            "subject",
            "lighting",
            "camera",
            "environment",
            "time_of_day",
            "hair_length",
            "hair_style",
            "hair_color",
            "outfit_type",
            "outfit_style",
            "outfit_color"
        ];

        mappings.forEach((key) => {
            const field = form.elements.namedItem(key);
            if (field && prompt[key] !== undefined && prompt[key] !== null) {
                field.value = prompt[key];
            }
        });

        generatedPrompt.value = prompt.generated_prompt;
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});

refreshPrompt();
