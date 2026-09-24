import mongoose from "mongoose";

const flowSchema = new mongoose.Schema(
    {
        srcIp: {
            type: String,
            required: true
        },

        dstIp: {
            type: String,
            required: true
        },

        srcPort: {
            type: Number,
            default: null
        },

        dstPort: {
            type: Number,
            default: null
        },

        protocol: {
            type: String,
            required: true
        },

        startTime: {
            type: Number,
            required: true
        },

        endTime: {
            type: Number,
            required: true
        },

        duration: {
            type: Number,
            required: true
        },

        prediction: {
            type: Number,
            required: true
        },

        phishingProbability: {
            type: Number,
            required: true
        },

        mlScore: {
            type: Number,
            required: true
        },

        ruleScore: {
            type: Number,
            required: true
        },

        finalScore: {
            type: Number,
            required: true
        },

        severity: {
            type: String,
            enum: [
                "LOW",
                "MEDIUM",
                "HIGH"
            ],
            required: true
        },

        classification: {
            type: String,
            enum: [
                "BENIGN",
                "SUSPICIOUS",
                "PHISHING"
            ],
            required: true
        },

        features: {
            type: mongoose.Schema.Types.Mixed,
            required: true
        }
    },
    {
        timestamps: true
    }
);

const Flow = mongoose.model(
    "Flow",
    flowSchema
);

export default Flow;
