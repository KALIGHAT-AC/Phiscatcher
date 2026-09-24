import Flow from "../models/Flow.js";

export const getLatestFlows = async (req, res) => {

    try {

        const flows = await Flow.find()
            .sort({ createdAt: -1 })
            .limit(5);

        res.status(200).json(flows);

    } catch (error) {

        console.error(
            "Error fetching flows:",
            error.message
        );

        res.status(500).json({
            message: "Failed to fetch flows"
        });
    }
};