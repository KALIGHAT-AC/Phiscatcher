import React from "react";
import { useEffect, useState } from "react";
import { io } from "socket.io-client";

import {
    Activity,
    ShieldCheck,
    AlertTriangle,
    Bug
} from "lucide-react";

import Header from "./components/Header";
import StatCard from "./components/StatCard";
import TrafficChart from "./components/TrafficChart";
import ThreatChart from "./components/ThreatChart";
import FlowTable from "./components/FlowTable";

import {
    getLatestFlows,
    getDashboardStats
} from "./services/api";

const SOCKET_URL = "http://localhost:8000";

function App() {
    // Latest 5 flows → charts + table
    const [recentFlows, setRecentFlows] = useState([]);

    // All flows → stat cards
    const [stats, setStats] = useState({
        total: 0,
        benign: 0,
        suspicious: 0,
        phishing: 0
    });

    const [loading, setLoading] = useState(true);

    // Initial dashboard data
    useEffect(() => {
        const loadDashboard = async () => {
            try {
                const [latestFlows, dashboardStats] =
                    await Promise.all([
                        getLatestFlows(),
                        getDashboardStats()
                    ]);

                setRecentFlows(latestFlows);
                setStats(dashboardStats);
            } catch (error) {
                console.error(
                    "Failed to load dashboard:",
                    error
                );
            } finally {
                setLoading(false);
            }
        };

        loadDashboard();
    }, []);

    // Socket.IO
    useEffect(() => {
        const socket = io(SOCKET_URL);

        socket.on("connect", () => {
            console.log(
                "Connected to Socket.IO:",
                socket.id
            );
        });

        socket.on("new-flow", (newFlow) => {
            console.log(
                "New flow received:",
                newFlow
            );

            // Keep only latest 5 flows
            setRecentFlows((currentFlows) => {
                const updated = [
                    newFlow,
                    ...currentFlows.filter(
                        (flow) => flow._id !== newFlow._id
                    )
                ];

                return updated.slice(0, 5);
            });

            // Update all-flow statistics
            setStats((currentStats) => {
                const updatedStats = {
                    ...currentStats,
                    total: currentStats.total + 1
                };

                if (newFlow.classification === "BENIGN") {
                    updatedStats.benign += 1;
                } else if (
                    newFlow.classification === "SUSPICIOUS"
                ) {
                    updatedStats.suspicious += 1;
                } else if (
                    newFlow.classification === "PHISHING"
                ) {
                    updatedStats.phishing += 1;
                }

                return updatedStats;
            });
        });

        socket.on("disconnect", () => {
            console.log(
                "Disconnected from Socket.IO"
            );
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    // Loading
    if (loading) {
        return (
            <div className="
                flex
                min-h-screen
                items-center
                justify-center
                bg-slate-950
                text-slate-400
            ">
                <div className="
                    flex
                    items-center
                    gap-3
                ">
                    <div className="
                        h-5
                        w-5
                        animate-spin
                        rounded-full
                        border-2
                        border-slate-700
                        border-t-indigo-400
                    " />

                    Loading dashboard...
                </div>
            </div>
        );
    }

    return (
        <main className="
            min-h-screen
            bg-slate-950
            bg-gradient-to-br
            from-slate-950
            via-indigo-950/30
            to-slate-950
            px-4
            py-6
            text-slate-100
            sm:px-6
            lg:px-8
        ">
            <div className="
                mx-auto
                max-w-[1600px]
            ">

                <Header />

                {/* STAT CARDS - ALL FLOWS */}
                <section className="
                    mt-8
                    grid
                    grid-cols-1
                    gap-4
                    sm:grid-cols-2
                    xl:grid-cols-4
                ">
                    <StatCard
                        title="Total Flows"
                        value={stats.total}
                        icon={Activity}
                        iconColor="text-indigo-400"
                        iconBackground="bg-indigo-500/10"
                    />

                    <StatCard
                        title="Benign"
                        value={stats.benign}
                        icon={ShieldCheck}
                        iconColor="text-emerald-400"
                        iconBackground="bg-emerald-400/10"
                    />

                    <StatCard
                        title="Suspicious"
                        value={stats.suspicious}
                        icon={AlertTriangle}
                        iconColor="text-amber-400"
                        iconBackground="bg-amber-400/10"
                    />

                    <StatCard
                        title="Phishing"
                        value={stats.phishing}
                        icon={Bug}
                        iconColor="text-red-400"
                        iconBackground="bg-red-400/10"
                    />
                </section>

                {/* CHARTS - LATEST 5 FLOWS */}
                <section className="
                    mt-6
                    grid
                    grid-cols-1
                    gap-6
                    xl:grid-cols-2
                ">
                    <TrafficChart
                        flows={recentFlows}
                    />

                    <ThreatChart
                        flows={recentFlows}
                    />
                </section>

                {/* TABLE - LATEST 5 FLOWS */}
                <section className="mt-6">
                    <FlowTable
                        flows={recentFlows}
                    />
                </section>

                <footer className="
                    mt-8
                    flex
                    flex-col
                    items-center
                    justify-between
                    gap-2
                    border-t
                    border-white/5
                    py-5
                    text-xs
                    text-slate-600
                    sm:flex-row
                ">
                    <p>
                        Phiscatcher
                    </p>

                    <p>
                        Real-time TShark + ML monitoring
                    </p>
                </footer>

            </div>
        </main>
    );
}

export default App;