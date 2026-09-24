import express from "express";

import dotenv from "dotenv";

import cors from "cors";

import {initialize} from "./socket/socket.js";

import http from "http";
import Flow from "./models/Flow.js";

import {
    startTshark,
    stopTshark
} from "./services/tsharkService.js";

import {
    startPython,
    stopPython,
    onFlowResult
} from "./services/pythonService.js";

import {
    calculateFinalScore
} from "./services/scoringService.js";

import connectDB from "./config/db.js";
import {getIO} from "./socket/socket.js";
import flowRoutes from "./routes/flowRoutes.js";
import dashboardRoutes from "./routes/dashboardRoutes.js";

dotenv.config();

const app = express();
connectDB();

const server = http.createServer(app);

initialize(server);

app.use(cors());

app.use(express.json());
app.use("/api/flows", flowRoutes);
app.use(
    "/api/dashboard",
    dashboardRoutes
);

const PORT = process.env.PORT || 8000;


// Receive completed flow from Python
onFlowResult(async (flow) => {

    console.log("\n========== FLOW ANALYSIS ==========");

    console.log("Source:", flow.srcIp);
    console.log("Destination:", flow.dstIp);
    console.log("Source Port:", flow.srcPort);
    console.log("Destination Port:", flow.dstPort);
    console.log("Protocol:", flow.protocol);

    console.log(
        "ML Probability:",
        flow.phishingProbability
    );

    const score = calculateFinalScore(flow);

    console.log("ML Score:", score.mlScore);
    console.log("Rule Score:", score.ruleScore);
    console.log("Final Score:", score.finalScore);
    console.log("Severity:", score.severity);
    console.log("Classification:", score.classification);


    // Save completed flow to MongoDB

    try {

        const savedFlow = await Flow.create({

            srcIp: flow.srcIp,
            dstIp: flow.dstIp,

            srcPort: flow.srcPort,
            dstPort: flow.dstPort,

            protocol: flow.protocol,

            startTime: flow.startTime,
            endTime: flow.endTime,
            duration: flow.duration,

            prediction: flow.prediction,
            phishingProbability:
                flow.phishingProbability,

            mlScore: score.mlScore,
            ruleScore: score.ruleScore,
            finalScore: score.finalScore,

            severity: score.severity,
            classification: score.classification,

            features: flow.features
        });
        let io;
        io = getIO();
        io.emit("new-flow", savedFlow);

        console.log(
            "Flow saved to MongoDB:",
            savedFlow._id
        );
        console.log(
    "Real-time event emitted: new-flow"
)

    } catch (error) {

        console.error(
            "Failed to save flow:",
            error.message
        );
    }


    console.log("===================================\n");
});


startPython();

setTimeout(() => {

    startTshark("5");

}, 1000);


server.listen(PORT, () => {

    console.log(`Server running on port ${PORT}`);

});


process.on("SIGINT", () => {

    console.log("\nShutting down...");

    stopTshark();

    stopPython();

    process.exit(0);

});

















