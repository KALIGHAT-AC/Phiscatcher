// src/components/ThreatChart.jsx
import React from "react";
import {
    PieChart,
    Pie,
    Cell,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function ThreatChart({ flows }) {
    const benign = flows.filter(
        (flow) => flow.classification === "BENIGN"
    ).length;

    const suspicious = flows.filter(
        (flow) => flow.classification === "SUSPICIOUS"
    ).length;

    const phishing = flows.filter(
        (flow) => flow.classification === "PHISHING"
    ).length;

    const data = [
        {
            name: "Benign",
            value: benign
        },
        {
            name: "Suspicious",
            value: suspicious
        },
        {
            name: "Phishing",
            value: phishing
        }
    ];

    const COLORS = [
        "#34d399",
        "#fbbf24",
        "#f87171"
    ];

    return (
        <div className="
            rounded-2xl
            border
            border-white/10
            bg-white/[0.04]
            p-5
            shadow-2xl
            backdrop-blur-xl
        ">
            <div className="mb-4">
                <h2 className="
                    text-lg
                    font-semibold
                    text-slate-100
                ">
                    Threat Distribution
                </h2>

                <p className="
                    text-sm
                    text-slate-500
                ">
                    Based on latest 5 flows
                </p>
            </div>

            <div className="h-[300px]">
                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >
                    <PieChart>
                        <Pie
                            data={data}
                            dataKey="value"
                            nameKey="name"
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            innerRadius={60}
                            paddingAngle={3}
                        >
                            {data.map((entry, index) => (
                                <Cell
                                    key={entry.name}
                                    fill={COLORS[index]}
                                />
                            ))}
                        </Pie>

                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#0f172a",
                                border: "1px solid rgba(255,255,255,0.1)",
                                borderRadius: "10px",
                                color: "#f8fafc"
                            }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export default ThreatChart;