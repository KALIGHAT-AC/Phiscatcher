import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";
import { EventEmitter } from "events";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const pythonEvents = new EventEmitter();

let pythonProcess = null;

export function startPython() {
    if (pythonProcess) {
        console.log("Python process is already running.");
        return;
    }

    const projectRoot = path.resolve(
        __dirname,
        "../../"
    );

    const pythonScript = path.join(
        projectRoot,
        "ml",
        "packet_processor.py"
    );

    console.log("Starting Python process...");
    console.log("Python script:", pythonScript);

    pythonProcess = spawn(
        "python",
        [pythonScript],
        {
            cwd: projectRoot
        }
    );

    let buffer = "";

    // ==========================================
    // PYTHON STDOUT
    // ==========================================

    pythonProcess.stdout.on("data", (data) => {

        buffer += data.toString();

        const lines = buffer.split("\n");

        buffer = lines.pop() || "";

        for (const line of lines) {

            const output = line.trim();

            if (!output) {
                continue;
            }

            console.log("Python:", output);

            try {

                const result = JSON.parse(output);

                // ----------------------------------
                // Flow result received
                // ----------------------------------

                if (
                    result.type === "flow_result"
                ) {

                    console.log(
                        "ML FLOW RESULT RECEIVED"
                    );

                    console.log(
                        "Prediction:",
                        result.prediction
                    );

                    console.log(
                        "Phishing Probability:",
                        result.phishingProbability
                    );

                    // Send result to rest of backend
                    pythonEvents.emit(
                        "flow_result",
                        result
                    );
                }

            } catch (error) {

                // Normal Python log
                // such as:
                // "Python packet processor started."

            }
        }
    });

    // ==========================================
    // PYTHON STDERR
    // ==========================================

    pythonProcess.stderr.on("data", (data) => {

        const error = data.toString().trim();

        if (error) {

            console.error(
                "Python Error:",
                error
            );
        }
    });

    // ==========================================
    // PYTHON ERROR
    // ==========================================

    pythonProcess.on("error", (error) => {

        console.error(
            "Failed to start Python:",
            error.message
        );

        pythonProcess = null;
    });

    // ==========================================
    // PYTHON CLOSED
    // ==========================================

    pythonProcess.on("close", (code) => {

        console.log(
            `Python process stopped with code ${code}`
        );

        pythonProcess = null;
    });
}


// ==============================================
// SEND PACKET TO PYTHON
// ==============================================

export function sendPacket(packet) {

    if (!pythonProcess) {

        console.error(
            "Python process is not running."
        );

        return;
    }

    try {

        const message =
            JSON.stringify(packet);

        pythonProcess.stdin.write(
            message + "\n"
        );

    } catch (error) {

        console.error(
            "Failed to send packet to Python:",
            error.message
        );
    }
}


// ==============================================
// LISTEN FOR FLOW RESULTS
// ==============================================

export function onFlowResult(callback) {

    pythonEvents.on(
        "flow_result",
        callback
    );
}


// ==============================================
// STOP PYTHON
// ==============================================

export function stopPython() {

    if (!pythonProcess) {

        console.log(
            "Python process is not running."
        );

        return;
    }

    console.log(
        "Stopping Python process..."
    );

    pythonProcess.kill();

    pythonProcess = null;
}