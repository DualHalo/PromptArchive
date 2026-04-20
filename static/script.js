function debounce(fn, delay = 300) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

const form = document.getElementById("promptForm");
const generatedPrompt = document.getElementById("generatedPrompt");
const generatedNegativePrompt = document.getElementById("generatedNegativePrompt");
const copyBtn = document.getElementById("copyBtn");
const copyNegativeBtn = document.getElementById("copyNegativeBtn");
const surpriseBtn = document.getElementById("surpriseBtn");
const clearBtn = document.getElementById("clearBtn");
const copiedPill = document.getElementById("copiedPill");
const copiedNegativePill = document.getElementById("copiedNegativePill");

const hairLengthSelect = document.getElementById("hair_length");
const hairStyleSelect = document.getElementById("hair_style");
const outfitTypeSelect = document.getElementById("outfit_type");
const outfitStyleSelect = document.getElementById("outfit_style");
const genderSelect = document.getElementById("gender");

const optionPools = {
    hairLength: {
        default: ["very short", "short", "medium-length", "long", "very long"],
        woman: ["very short", "short", "medium-length", "long", "very long"],
        man: ["bald", "buzzed", "very short", "short", "medium-length", "long", "very long"],
        "non-binary": ["bald", "buzzed", "very short", "short", "medium-length", "long", "very long"]
    },
    hairStyle: {
        default: [
            "sleek straight",
            "soft wavy",
            "loose curls",
            "messy bun",
            "side-swept layers",
            "braided"
        ],
        woman: [
            "sleek straight",
            "soft wavy",
            "loose curls",
            "messy bun",
            "high ponytail",
            "low ponytail",
            "side-swept layers",
            "romantic updo",
            "braid crown",
            "long layered blowout",
            "shoulder-length bob",
            "voluminous curls"
        ],
        man: [
            "short textured cut",
            "side part",
            "slicked back",
            "pompadour",
            "crew cut",
            "taper fade",
            "undercut",
            "wavy medium cut"
        ],
        "non-binary": [
            "sleek straight",
            "soft wavy",
            "short textured cut",
            "side part",
            "messy bun",
            "braided",
            "undercut",
            "shoulder-length bob"
        ]
    },
    outfitType: {
        default: [
            "structured blazer",
            "streetwear look",
            "casual outfit",
            "athletic wear",
            "luxury fashion outfit"
        ],
        woman: [
            "dress",
            "gown",
            "cocktail dress",
            "summer dress",
            "blazer ensemble",
            "streetwear look",
            "casual outfit",
            "athletic wear",
            "eveningwear",
            "luxury fashion outfit"
        ],
        man: [
            "tailored suit",
            "tuxedo",
            "blazer and slacks",
            "business suit",
            "casual menswear",
            "streetwear look",
            "athletic wear",
            "luxury fashion outfit"
        ],
        "non-binary": [
            "structured blazer",
            "tailored suit",
            "streetwear look",
            "casual outfit",
            "athletic wear",
            "luxury fashion outfit"
        ]
    },
    outfitStyle: {
        default: [
            "elegant",
            "editorial",
            "tailored",
            "minimalist",
            "luxury"
        ],
        woman: [
            "elegant",
            "glamorous",
            "editorial",
            "tailored",
            "chic",
            "romantic",
            "luxury",
            "high fashion"
        ],
        man: [
            "tailored",
            "sharp",
            "editorial",
            "luxury",
            "minimalist",
            "classic",
            "modern"
        ],
        "non-binary": [
            "editorial",
            "tailored",
            "minimalist",
            "luxury",
            "avant-garde",
            "modern"
        ]
    }
};

const surpriseSets = {
    subject_type: ["Portrait", "Fashion", "Fantasy", "Lifestyle", "Group"],
    gender: ["Woman", "Man", "Non-binary"],
    shot_type: [
        "Extreme close-up",
        "Headshot",
        "Tight portrait",
        "Chest-up",
        "Waist-up",
        "3/4 body",
        "Full body",
        "Wide shot",
        "Environmental portrait"
    ],
    locale: ["New York City", "Tokyo", "Paris", "Austin", "Los Angeles"],
    subject: [
        "business executive",
        "fantasy warrior",
        "luxury model",
        "cinematic protagonist",
        "fashion editor"
    ],
    lighting: [
        "soft natural lighting",
        "soft diffused window light",
        "golden hour glow",
        "dramatic studio lighting",
        "moody cinematic lighting"
    ],
    camera: [
        "85mm portrait lens",
        "50mm prime lens",
        "35mm cinematic lens",
        "cinematic anamorphic lens",
        "medium format photography"
    ],
    environment: [
        "modern apartment interior",
        "luxury rooftop terrace",
        "lush botanical garden",
        "moody candlelit lounge",
        "sunlit beach boardwalk"
    ],
    time_of_day: ["morning", "afternoon", "golden hour", "sunset", "night"],
    age_range: ["18–24", "25–34", "35–44", "45–54", "55+"],
    eye_color: ["brown", "hazel", "green", "blue", "gray"],
    skin_tone: [
        "fair with cool undertones",
        "light olive complexion",
        "medium tan complexion",
        "warm brown skin",
        "deep brown skin"
    ],
    heritage_notes: [
        "Latina features",
        "Mediterranean facial structure",
        "East Asian appearance",
        "Afro-Caribbean features",
        "mixed-race appearance"
    ],
    body_shape: ["slim", "lean", "athletic", "curvy", "soft hourglass", "broad-shouldered"],
    expression: [
        "soft smile",
        "confident expression",
        "playful expression",
        "mysterious expression",
        "intense gaze"
    ],
    hair_color: [
        "dark brown with soft highlights",
        "jet black",
        "warm auburn",
        "chestnut brown",
        "dark blonde"
    ],
    outfit_color: ["black", "charcoal", "navy", "ivory", "emerald green"]
};

function randomItem(items) {
    return items[Math.floor(Math.random() * items.length)];
}

function populateSelect(selectEl, placeholder, values, preserveValue = "") {
    const currentValue = preserveValue || "";
    selectEl.innerHTML = "";

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;
    selectEl.appendChild(placeholderOption);

    values.forEach((value) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        selectEl.appendChild(option);
    });

    if (currentValue && values.includes(currentValue)) {
        selectEl.value = currentValue;
    } else {
        selectEl.value = "";
    }
}

function applyGenderAwareOptions() {
    const gender = genderSelect.value.toLowerCase() || "default";

    populateSelect(
        hairLengthSelect,
        "-- Select Hair Length --",
        optionPools.hairLength[gender] || optionPools.hairLength.default,
        hairLengthSelect.value
    );

    populateSelect(
        hairStyleSelect,
        "-- Select Hairstyle --",
        optionPools.hairStyle[gender] || optionPools.hairStyle.default,
        hairStyleSelect.value
    );

    populateSelect(
        outfitTypeSelect,
        "-- Select Outfit Type --",
        optionPools.outfitType[gender] || optionPools.outfitType.default,
        outfitTypeSelect.value
    );

    populateSelect(
        outfitStyleSelect,
        "-- Select Outfit Style --",
        optionPools.outfitStyle[gender] || optionPools.outfitStyle.default,
        outfitStyleSelect.value
    );
}

async function refreshPrompt() {
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });

    const data = await response.json();
    generatedPrompt.value = data.prompt || "";
    generatedNegativePrompt.value = data.negative_prompt || "";
}

const debouncedRefreshPrompt = debounce(refreshPrompt, 300);

function flashPill(pill) {
    pill.classList.add("show");
    window.setTimeout(() => pill.classList.remove("show"), 1200);
}

form.addEventListener("input", debouncedRefreshPrompt);
form.addEventListener("change", refreshPrompt);

genderSelect.addEventListener("change", async () => {
    applyGenderAwareOptions();
    await refreshPrompt();
});

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
            if (field.tagName === "SELECT") {
                field.value = randomItem(values);
            } else {
                field.value = randomItem(values);
            }
        }
    });

    applyGenderAwareOptions();

    if (hairLengthSelect.options.length > 1) {
        hairLengthSelect.value = randomItem(
            Array.from(hairLengthSelect.options).slice(1).map((option) => option.value)
        );
    }

    if (hairStyleSelect.options.length > 1) {
        hairStyleSelect.value = randomItem(
            Array.from(hairStyleSelect.options).slice(1).map((option) => option.value)
        );
    }

    if (outfitTypeSelect.options.length > 1) {
        outfitTypeSelect.value = randomItem(
            Array.from(outfitTypeSelect.options).slice(1).map((option) => option.value)
        );
    }

    if (outfitStyleSelect.options.length > 1) {
        outfitStyleSelect.value = randomItem(
            Array.from(outfitStyleSelect.options).slice(1).map((option) => option.value)
        );
    }

    await refreshPrompt();
});

clearBtn.addEventListener("click", () => {
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

    applyGenderAwareOptions();

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

        const directMappings = [
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
            "age_range",
            "eye_color",
            "skin_tone",
            "heritage_notes",
            "body_shape",
            "expression",
            "hair_color",
            "outfit_color"
        ];

        directMappings.forEach((key) => {
            const field = form.elements.namedItem(key);
            if (field && prompt[key] !== undefined && prompt[key] !== null) {
                field.value = prompt[key];
            }
        });

        applyGenderAwareOptions();

        const genderAwareMappings = [
            "hair_length",
            "hair_style",
            "outfit_type",
            "outfit_style"
        ];

        genderAwareMappings.forEach((key) => {
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

applyGenderAwareOptions();
refreshPrompt();