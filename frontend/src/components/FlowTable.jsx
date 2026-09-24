import { Activity } from "lucide-react";
import React from "react";

function formatTime(time) {

    if (!time) {
        return "--";
    }

    const date = new Date(time);

    return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });
}

function Score({ value }) {

    let color = "text-emerald-400";

    if (value >= 75) {
        color = "text-red-400";
    } else if (value >= 40) {
        color = "text-amber-400";
    }

    return (
        <span className={`font-semibold ${color}`}>
            {Number(value || 0).toFixed(1)}
        </span>
    );
}

function StatusBadge({ status }) {

    const styles = {
        BENIGN: `
            border-emerald-400/20
            bg-emerald-400/10
            text-emerald-400
        `,

        SUSPICIOUS: `
            border-amber-400/20
            bg-amber-400/10
            text-amber-400
        `,

        PHISHING: `
            border-red-400/20
            bg-red-400/10
            text-red-400
        `
    };

    return (
        <span className={`
            inline-flex
            items-center
            rounded-full
            border
            px-3
            py-1
            text-[10px]
            font-bold
            tracking-wider
            ${styles[status] || styles.BENIGN}
        `}>
            {status}
        </span>
    );
}

function FlowTable({ flows }) {

    return (
        <div className="
            overflow-hidden
            rounded-2xl
            border border-white/10
            bg-white/[0.04]
            shadow-2xl
            backdrop-blur-xl
        ">

            <div className="
                flex
                items-center
                justify-between
                border-b border-white/10
                px-6
                py-5
            ">

                <div>

                    <h2 className="
                        text-base
                        font-semibold
                        text-white
                    ">
                        Latest 5 Flows
                    </h2>

                    <p className="
                        mt-1
                        text-sm
                        text-slate-500
                    ">
                        Most recent analyzed network flows
                    </p>

                </div>

                <Activity
                    size={20}
                    className="text-indigo-400"
                />

            </div>

            <div className="overflow-x-auto">

                <table className="w-full min-w-[950px]">

                    <thead>

                        <tr className="
                            border-b
                            border-white/5
                            text-left
                        ">

                            <th className="table-heading">
                                Time
                            </th>

                            <th className="table-heading">
                                Source
                            </th>

                            <th className="table-heading">
                                Destination
                            </th>

                            <th className="table-heading">
                                Protocol
                            </th>

                            <th className="table-heading">
                                ML Score
                            </th>

                            <th className="table-heading">
                                JS Rule Score
                            </th>

                            <th className="table-heading">
                                Final Score
                            </th>

                            <th className="table-heading">
                                Status
                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {flows.length === 0 ? (

                            <tr>

                                <td
                                    colSpan="8"
                                    className="
                                        px-6
                                        py-16
                                        text-center
                                        text-sm
                                        text-slate-500
                                    "
                                >
                                    No flows detected yet.
                                </td>

                            </tr>

                        ) : (

                            flows.map((flow) => (

                                <tr
                                    key={flow._id}
                                    className="
                                        border-b
                                        border-white/5
                                        transition-colors
                                        hover:bg-white/[0.035]
                                    "
                                >

                                    <td className="
                                        px-6
                                        py-4
                                        text-xs
                                        text-slate-400
                                    ">
                                        {formatTime(
                                            flow.createdAt ||
                                            flow.startTime
                                        )}
                                    </td>

                                    <td className="
                                        px-6
                                        py-4
                                        font-mono
                                        text-xs
                                        text-slate-300
                                    ">
                                        {flow.srcIp}
                                    </td>

                                    <td className="
                                        px-6
                                        py-4
                                        font-mono
                                        text-xs
                                        text-slate-300
                                    ">
                                        {flow.dstIp}
                                    </td>

                                    <td className="
                                        px-6
                                        py-4
                                        text-xs
                                        font-medium
                                        text-slate-400
                                    ">
                                        {flow.protocol}
                                    </td>

                                    <td className="px-6 py-4 text-xs">
                                        <Score
                                            value={flow.mlScore}
                                        />
                                    </td>

                                    <td className="px-6 py-4 text-xs">
                                        <Score
                                            value={flow.ruleScore}
                                        />
                                    </td>

                                    <td className="px-6 py-4 text-xs">
                                        <Score
                                            value={flow.finalScore}
                                        />
                                    </td>

                                    <td className="px-6 py-4">
                                        <StatusBadge
                                            status={
                                                flow.classification
                                            }
                                        />
                                    </td>

                                </tr>

                            ))

                        )}

                    </tbody>

                </table>

            </div>

        </div>
    );
}

export default FlowTable;