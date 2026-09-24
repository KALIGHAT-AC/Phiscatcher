import Flow from "../models/Flow.js";

export const getDashboardStats = async (req, res) => {

    try {

        const total = await Flow.countDocuments();

        const benign = await Flow.countDocuments({
            classification: "BENIGN"
        });

        const suspicious = await Flow.countDocuments({
            classification: "SUSPICIOUS"
        });

        const phishing = await Flow.countDocuments({
            classification: "PHISHING"
        });

        res.status(200).json({
            total,
            benign,
            suspicious,
            phishing
        });

    } catch (error) {

        console.error(
            "Error fetching dashboard stats:",
            error.message
        );

        res.status(500).json({
            message: "Failed to fetch dashboard statistics"
        });

    }

};