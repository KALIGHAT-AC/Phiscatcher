import React from "react";
function StatCard({
    title,
    value,
    icon: Icon,
    iconColor,
    iconBackground
}) {

    return (
        <div className="
            group
            rounded-2xl
            border border-white/10
            bg-white/[0.04]
            p-5
            shadow-2xl
            backdrop-blur-xl
            transition-all
            duration-300
            hover:-translate-y-1
            hover:border-indigo-400/20
            hover:bg-white/[0.06]
        ">

            <div className="flex items-start justify-between">

                <div>

                    <p className="
                        text-xs
                        font-medium
                        uppercase
                        tracking-wider
                        text-slate-500
                    ">
                        {title}
                    </p>

                    <p className="
                        mt-3
                        text-3xl
                        font-bold
                        tracking-tight
                        text-white
                    ">
                        {value}
                    </p>

                </div>

                <div
                    className={`
                        flex h-11 w-11
                        items-center justify-center
                        rounded-xl
                        ${iconBackground}
                    `}
                >
                    <Icon
                        size={21}
                        className={iconColor}
                    />
                </div>

            </div>

        </div>
    );
}

export default StatCard;