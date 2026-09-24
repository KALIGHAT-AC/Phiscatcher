import { Activity, ShieldCheck } from "lucide-react";
import React from "react";

function Header() {
    return (
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

            <div className="flex items-center gap-4">

                <div className="
                    flex h-12 w-12 items-center justify-center
                    rounded-xl
                    border border-indigo-400/20
                    bg-indigo-500/10
                    shadow-lg shadow-indigo-950/30
                ">
                    <ShieldCheck
                        size={26}
                        className="text-indigo-400"
                    />
                </div>

                <div>
                    <h1 className="
                        text-2xl
                        font-bold
                        tracking-tight
                        text-white
                    ">
                        Phiscatcher
                    </h1>

                    <p className="
                        mt-1
                        text-sm
                        text-slate-400
                    ">
                        Real-time network threat monitoring
                    </p>
                </div>

            </div>

            <div className="
                flex
                w-fit
                items-center
                gap-2
                rounded-full
                border border-emerald-400/20
                bg-emerald-400/10
                px-4
                py-2
            ">

                <span className="
                    h-2
                    w-2
                    animate-pulse
                    rounded-full
                    bg-emerald-400
                    shadow-lg
                    shadow-emerald-400/50" />

                <Activity
                    size={15}
                    className="text-emerald-400"
                />

                <span className="
                    text-xs
                    font-semibold
                    tracking-wider
                    text-emerald-400
                ">
                    LIVE
                </span>

            </div>

        </header>
    );
}

export default Header;