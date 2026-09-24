// ==========================================
// RULE ENGINE
// ==========================================

function calculateRuleScore(flow) {

    let score = 0;

    const probability =
        flow.phishingProbability;

    // --------------------------------------
    // High ML probability
    // --------------------------------------

    if (probability >= 0.80) {

        score += 40;

    } else if (probability >= 0.60) {

        score += 25;

    } else if (probability >= 0.40) {

        score += 10;
    }


    // --------------------------------------
    // Suspicious ports
    // --------------------------------------

    const suspiciousPorts = [
        21,
        23,
        25,
        445,
        3389
    ];

    if (
        suspiciousPorts.includes(
            flow.dstPort
        )
    ) {

        score += 15;
    }


    // --------------------------------------
    // Suspicious DNS domain
    // --------------------------------------

    const domain =
        flow.features?.dns_second_level_domain ||
        "";

    const suspiciousWords = [
        "login",
        "verify",
        "secure",
        "account",
        "update",
        "confirm",
        "wallet"
    ];

    for (const word of suspiciousWords) {

        if (
            domain
                .toLowerCase()
                .includes(word)
        ) {

            score += 20;

            break;
        }
    }


    return Math.min(
        score,
        100
    );
}


// ==========================================
// FINAL SCORE
// ==========================================

export function calculateFinalScore(flow) {

    const mlScore =
        flow.phishingProbability * 100;

    const ruleScore =
        calculateRuleScore(flow);

    // ML gets 70%
    // Rules get 30%

    const finalScore =
        (mlScore * 0.7) +
        (ruleScore * 0.3);

    let severity;

    if (finalScore >= 75) {

        severity = "HIGH";

    } else if (finalScore >= 40) {

        severity = "MEDIUM";

    } else {

        severity = "LOW";
    }

    let classification; if (finalScore >= 75) { classification = "PHISHING"; } else if (finalScore >= 40) { classification = "SUSPICIOUS"; } else { classification = "BENIGN"; }

    return {

        mlScore,

        ruleScore,

        finalScore,

        severity,

        classification
           
    };
}