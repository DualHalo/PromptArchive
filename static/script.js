const form = document.getElementById("promptForm");
const generatedPrompt = document.getElementById("generatedPrompt");
const generatedNegativePrompt = document.getElementById("generatedNegativePrompt");
const copyBtn = document.getElementById("copyBtn");
const copyNegativeBtn = document.getElementById("copyNegativeBtn");
const surpriseBtn = document.getElementById("surpriseBtn");
const clearBtn = document.getElementById("clearBtn");
const copiedPill = document.getElementById("copiedPill");
const copiedNegativePill = document.getElementById("copiedNegativePill");

const surpriseSets = {
    subject_type: [
        "Portrait",
        "Fashion",
        "Fantasy",
        "Lifestyle",
        "Group"
    ],
    gender: [
        "Woman",
        "Man",
        "Non-binary"
    ],
    shot_type: [
        "Headshot",
        "Portrait (Chest-Up)",
        "3/4 Body",
        "Full Body"
    ],
    locale: [
        "New York City",
        "Tokyo",
        "Paris",
        "Austin",
        "Los Angeles"
    ],
    subject: [
        "confident fashion model",
        "mysterious fantasy heroine",
        "luxury lifestyle influencer",
        "elegant business executive",
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
    ],
    eye_color: [
    "brown",
    "hazel",
    "green",
    "blue",
    "gray"
    ],
    expression: [
        "soft smile",
        "confident expression",
        "playful expression",
        "mysterious expression",
        "intense gaze"
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
    generatedPrompt.value = data.prompt || "";
    generatedNegativePrompt.value = data.negative_prompt || "";
}

function flashPill(pill) {
    pill.classList.add("show");
    window.setTimeout(() => pill.classList.remove("show"), 1200);
}

form.addEventListener("input", refreshPrompt);
form.addEventListener("change", refreshPrompt);

copyBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(generatedPrompt.value);
    flashPill(copiedPill);
});

copyNegativeBtn.addEventListener("click", async () => {
    await navigator.clipboard.writeText(generatedNegativePrompt.value);
    flashPill(copiedNegativePill);
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

clearBtn.addEventListener("click", async () => {
    if (!confirm("Clear all fields and start fresh?")) return;

    Array.from(form.elements).forEach((el) => {
        if (!el.name) return;

        if (el.tagName === "INPUT") {
            el.value = "";
        }

        if (el.tagName === "SELECT") {
            el.selectedIndex = 0;
        }

        if (el.tagName === "TEXTAREA") {
            el.value = "";
        }
    });

    generatedPrompt.value = "";
    generatedNegativePrompt.value = "";

    window.scrollTo({ top: 0, behavior: "smooth" });
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
            "subject_type",
            "gender",
            "shot_type",
            "locale",
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
            "outfit_color",
            "eye_color",
            "expression"
        ];

        mappings.forEach((key) => {
            const field = form.elements.namedItem(key);
            if (field && prompt[key] !== undefined && prompt[key] !== null) {
                field.value = prompt[key];
            }
        });

        generatedPrompt.value = prompt.generated_prompt || "";
        generatedNegativePrompt.value = prompt.negative_prompt || "";
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});

refreshPrompt();