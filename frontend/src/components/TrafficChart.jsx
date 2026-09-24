import React from "react";
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip
} from "recharts";

function TrafficChart({ flows }) {

    const data = flows
        .slice()
        .reverse()
        .map((flow, index) => ({
            name: index + 1,
            flows: index + 1
        }));

    return (
        <div className="
            rounded-2xl
            border border-white/10
            bg-white/[0.04]
            p-6
            shadow-2xl
            backdrop-blur-xl
        ">

            <div className="mb-6">

                <h2 className="
                    text-base
                    font-semibold
                    text-white
                ">
                    Traffic Analysis
                </h2>

                <p className="
                    mt-1
                    text-sm
                    text-slate-500
                ">
                    Flow activity over recent traffic
                </p>

            </div>

            <div className="h-[280px]">

                <ResponsiveContainer
                    width="100%"
                    height="100%"
                >

                    <AreaChart data={data}>

                        <defs>
                            <linearGradient
                                id="trafficGradient"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="0%"
                                    stopOpacity={0.35}
                                />

                                <stop
                                    offset="100%"
                                    stopOpacity={0}
                                />
                            </linearGradient>
                        </defs>

                        <CartesianGrid
                            stroke="rgba(255,255,255,0.05)"
                            vertical={false}
                        />

                        <XAxis
                            dataKey="name"
                            tick={{
                                fill: "#64748b",
                                fontSize: 11
                            }}
                            axisLine={false}
                            tickLine={false}
                        />

                        <YAxis
                            tick={{
                                fill: "#64748b",
                                fontSize: 11
                            }}
                            axisLine={false}
                            tickLine={false}
                            allowDecimals={false}
                        />

                        <Tooltip
                            contentStyle={{
                                background: "#0f172a",
                                border: "1px solid rgba(255,255,255,0.1)",
                                borderRadius: "12px",
                                color: "#fff"
                            }}
                        />

                        <Area
                            type="monotone"
                            dataKey="flows"
                            stroke="#818cf8"
                            strokeWidth={2}
                            fill="url(#trafficGradient)"
                        />

                    </AreaChart>

                </ResponsiveContainer>

            </div>

        </div>
    );
}

export default TrafficChart;