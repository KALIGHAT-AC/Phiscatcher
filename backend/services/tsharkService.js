import { spawn } from "child_process";
import { sendPacket } from "./pythonService.js";

const TSHARK_PATH = "C:\\Program Files\\Wireshark\\tshark.exe";

let tsharkProcess = null;

export function startTshark(interfaceNumber = "5") {
    if (tsharkProcess) {
        console.log("TShark is already running.");
        return;
    }

    console.log(`Starting TShark on interface ${interfaceNumber}...`);

    tsharkProcess = spawn(
        TSHARK_PATH,
        [
            "-i", interfaceNumber,

            // Live output
            "-l",

            // Fields output
            "-T", "fields",

            // Timestamp
            "-e", "frame.time_epoch",

            // Packet length
            "-e", "frame.len",

            // IPv4
            "-e", "ip.src",
            "-e", "ip.dst",
            "-e", "ip.proto",
            "-e", "ip.ttl",

            // IPv6
            "-e", "ipv6.src",
            "-e", "ipv6.dst",
            "-e", "ipv6.nxt",
            "-e", "ipv6.hlim",

            // TCP
            "-e", "tcp.srcport",
            "-e", "tcp.dstport",

            // UDP
            "-e", "udp.srcport",
            "-e", "udp.dstport",

            // DNS
            "-e", "dns.qry.name",
            "-e", "dns.qry.type",

            // Output formatting
            "-E", "separator=|",
            "-E", "quote=n",
            "-E", "header=n"
        ]
    );

    // ========================================================
    // STDOUT BUFFER
    // ========================================================

    let buffer = "";

    tsharkProcess.stdout.on("data", (data) => {

        buffer += data.toString();

        const lines = buffer.split("\n");

        // Keep incomplete line for next chunk
        buffer = lines.pop() || "";

        for (const line of lines) {

            const trimmedLine = line.trim();

            if (!trimmedLine) {
                continue;
            }

            try {

                const fields = trimmedLine.split("|");

                /*
                    Field order:

                    0  frame.time_epoch
                    1  frame.len

                    2  ip.src
                    3  ip.dst
                    4  ip.proto
                    5  ip.ttl

                    6  ipv6.src
                    7  ipv6.dst
                    8  ipv6.nxt
                    9  ipv6.hlim

                    10 tcp.srcport
                    11 tcp.dstport

                    12 udp.srcport
                    13 udp.dstport

                    14 dns.qry.name
                    15 dns.qry.type
                */

                const [
                    timestamp,
                    packetLength,

                    ipv4Src,
                    ipv4Dst,
                    ipv4Protocol,
                    ipv4Ttl,

                    ipv6Src,
                    ipv6Dst,
                    ipv6Protocol,
                    ipv6Ttl,

                    tcpSrcPort,
                    tcpDstPort,

                    udpSrcPort,
                    udpDstPort,

                    dnsQuery,
                    dnsQueryType
                ] = fields;

                // =================================================
                // IP ADDRESS
                // =================================================

                const srcIp =
                    ipv4Src ||
                    ipv6Src ||
                    null;

                const dstIp =
                    ipv4Dst ||
                    ipv6Dst ||
                    null;

                // =================================================
                // PROTOCOL
                // =================================================

                const protocol =
                    ipv4Protocol ||
                    ipv6Protocol ||
                    null;

                // =================================================
                // TTL / HOP LIMIT
                // =================================================

                const ttl =
                    ipv4Ttl ||
                    ipv6Ttl ||
                    null;

                // =================================================
                // PORTS
                // =================================================

                const srcPort =
                    tcpSrcPort ||
                    udpSrcPort ||
                    null;

                const dstPort =
                    tcpDstPort ||
                    udpDstPort ||
                    null;

                // =================================================
                // CREATE PACKET OBJECT
                // =================================================

                const packet = {

                    timestamp:
                        timestamp || null,

                    packetLength:
                        Number(packetLength) || 0,

                    srcIp,

                    dstIp,

                    srcPort:
                        Number(srcPort) || null,

                    dstPort:
                        Number(dstPort) || null,

                    protocol,

                    ttl:
                        ttl || null,

                    dnsQuery:
                        dnsQuery || null,

                    dnsQueryType:
                        dnsQueryType || null
                };

                // =================================================
                // SEND TO PYTHON
                // =================================================

                sendPacket(packet);

                // Optional debugging
                console.log("PACKET:", packet);

            } catch (error) {

                console.error(
                    "Error parsing TShark packet:",
                    error.message
                );
            }
        }
    });

    // ========================================================
    // STDERR
    // ========================================================

    tsharkProcess.stderr.on("data", (data) => {

        const message = data
            .toString()
            .trim();

        if (message) {
            console.error(
                "TShark:",
                message
            );
        }
    });

    // ========================================================
    // PROCESS ERROR
    // ========================================================

    tsharkProcess.on("error", (error) => {

        console.error(
            "Failed to start TShark:",
            error.message
        );

        tsharkProcess = null;
    });

    // ========================================================
    // PROCESS CLOSED
    // ========================================================

    tsharkProcess.on("close", (code) => {

        console.log(
            `TShark stopped with code ${code}`
        );

        tsharkProcess = null;
    });

    console.log("TShark started successfully.");
}


// ============================================================
// STOP TSHARK
// ============================================================

export function stopTshark() {

    if (!tsharkProcess) {

        console.log(
            "TShark is not running."
        );

        return;
    }

    console.log(
        "Stopping TShark..."
    );

    tsharkProcess.kill();

    tsharkProcess = null;
}