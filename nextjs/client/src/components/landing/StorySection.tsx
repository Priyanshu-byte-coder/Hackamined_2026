import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

const storyPanels = [
    {
        bg: 'var(--color-brand-primary)', text: 'var(--color-text-inverse)', num: '01',
        headline: 'Why This is a Massive Industry Problem',
        body: (
            <div className="space-y-4">
                <p>When a solar inverter—the critical component that converts electricity from solar panels into usable power—fails, it directly causes energy loss, lower uptime, and significant financial hits. To give you an idea of the scale based on recent industry research:</p>
                <ul className="list-disc pl-5 space-y-2 lg:space-y-3">
                    <li><strong>Multi-Billion Dollar Losses:</strong> The solar industry lost roughly $4.6 billion in a single year (2023) due to equipment underperformance globally.</li>
                    <li><strong>High Failure Rates:</strong> Inverters are the beating heart of a solar system but also the most vulnerable, accounting for approximately 17% of total fault incidents in solar PV farms.</li>
                </ul>
            </div>
        ),
    },
    {
        bg: 'var(--color-bg-secondary)', text: 'var(--color-text-primary)', num: '02',
        headline: 'The Cost of Extended Inverter Downtime',
        body: (
            <div className="space-y-4">
                <p>The impact of a failed inverter extends far beyond the initial breakdown. Without predictive intelligence, resolution is painfully slow:</p>
                <ul className="list-disc pl-5 space-y-2 lg:space-y-3">
                    <li><strong>Prolonged Downtime:</strong> Major inverter failures result in an average downtime of 80 days, often costing upwards of $49,000 per incident due to lengthy repair times and lost business revenue.</li>
                    <li><strong>Energy Drain:</strong> Research from the National Renewable Energy Laboratory (NREL) indicates that inverter failures can cause up to 36% of total energy losses in a solar plant over a multi-year period.</li>
                </ul>
            </div>
        ),
    },
    {
        bg: 'var(--color-brand-primary)', text: 'var(--color-text-inverse)', num: '03',
        headline: 'Architecting an Industry-Standard Solution',
        body: (
            <div className="space-y-4">
                <p>To build a solution that establishes an industry standard, your system needs to move beyond simple exploratory analysis to a production-ready deployment. Here is the blueprint for an elite-level solution:</p>
                <ul className="list-disc pl-5 space-y-2 lg:space-y-3">
                    <li><strong>Advanced ML Pipeline:</strong> Develop a robust binary classification or regression model using telemetry, computed KPIs, and alarm data. Implement time-series aware walk-forward validation.</li>
                    <li><strong>Deep Explainability:</strong> Black-box models don't work in industrial settings. Integrate SHAP or LIME to provide clear feature importance for at least the top 5 contributing factors.</li>
                </ul>
            </div>
        ),
    },
    {
        bg: 'var(--color-bg-secondary)', text: 'var(--color-text-primary)', num: '04',
        headline: 'Agentic Workflows & Actionable Dashboards',
        body: (
            <div className="space-y-4">
                <p>The final puzzle piece is translating raw machine learning outputs into operational insights that technicians can immediately trust and act upon:</p>
                <ul className="list-disc pl-5 space-y-2 lg:space-y-3">
                    <li><strong>Agentic GenAI Layer:</strong> Build a RAG system with strict hallucination guardrails that grounds its answers in actual inverter data to autonomously draft maintenance tickets.</li>
                    <li><strong>Production-Grade Backend:</strong> Containerize the application with Docker and expose predictions via a well-architected REST API.</li>
                    <li><strong>Actionable Dashboard:</strong> Build a responsive frontend that visualizes per-inverter risk scores, trend data, and GenAI narratives with absolute clarity.</li>
                </ul>
            </div>
        ),
    },
];

export const StorySection = () => {
    const trackRef = useRef<HTMLDivElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);

    // Fallback for mobile
    const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;

    useEffect(() => {
        if (isMobile) return;

        // CRITICAL: Kill any existing ScrollTrigger instances for this section first
        ScrollTrigger.getAll().forEach(t => {
            if (t.vars.trigger === containerRef.current) t.kill();
        });

        const panels = gsap.utils.toArray('.story-panel');
        const totalWidth = panels.length * window.innerWidth;

        const ctx = gsap.context(() => {
            gsap.to(trackRef.current, {
                x: () => -(totalWidth - window.innerWidth),
                ease: 'none',
                scrollTrigger: {
                    trigger: containerRef.current,
                    pin: true,
                    scrub: 1.2,
                    snap: {
                        snapTo: 1 / (panels.length - 1),
                        duration: { min: 0.3, max: 0.6 },
                        ease: 'power2.inOut'
                    },
                    // CRITICAL: end must be dynamic, not fixed pixels
                    end: () => `+=${totalWidth - window.innerWidth}`,
                    invalidateOnRefresh: true,
                }
            });

            // Panel Enter Animations (clip path text reveal)
            panels.forEach((panel: any, i) => {
                const headline = panel.querySelector('.panel-headline');
                const body = panel.querySelector('.panel-body');

                // Setup initial state
                gsap.set(headline, { clipPath: 'inset(0 100% 0 0)', opacity: 0, x: 40 });
                gsap.set(body, { clipPath: 'inset(0 100% 0 0)', opacity: 0, x: 60 });

                ScrollTrigger.create({
                    trigger: containerRef.current,
                    start: () => `top top-=${i * window.innerWidth - window.innerWidth / 2}`,
                    end: () => `top top-=${i * window.innerWidth + window.innerWidth / 2}`,
                    onEnter: () => {
                        gsap.to(headline, { clipPath: 'inset(0 0% 0 0)', opacity: 1, x: 0, duration: 0.7, ease: "power3.out" });
                        gsap.to(body, { clipPath: 'inset(0 0% 0 0)', opacity: 1, x: 0, duration: 0.7, delay: 0.1, ease: "power3.out" });
                    },
                    onEnterBack: () => {
                        gsap.to(headline, { clipPath: 'inset(0 0% 0 0)', opacity: 1, x: 0, duration: 0.7, ease: "power3.out" });
                        gsap.to(body, { clipPath: 'inset(0 0% 0 0)', opacity: 1, x: 0, duration: 0.7, delay: 0.1, ease: "power3.out" });
                    }
                });
            });
        }, containerRef);

        return () => {
            ctx.revert();
        };
    }, [isMobile]);

    if (isMobile) {
        return (
            <div className="flex flex-col">
                {storyPanels.map((panel, i) => (
                    <div key={i} style={{ backgroundColor: panel.bg, color: panel.text, padding: '80px 24px', position: 'relative' }}>
                        <div style={{
                            position: 'absolute', top: 20, right: 20,
                            fontFamily: 'var(--font-display)', fontSize: '20vw', color: panel.text, opacity: 0.06, lineHeight: 1
                        }}>
                            {panel.num}
                        </div>
                        <h2 style={{ fontFamily: 'var(--font-display)', fontSize: 'clamp(3rem, 12vw, 4rem)', marginBottom: '16px', lineHeight: 1 }}>
                            {panel.headline}
                        </h2>
                        <div style={{ fontFamily: 'var(--font-body)', fontSize: '1rem', lineHeight: 1.6, opacity: 0.9 }}>
                            {panel.body}
                        </div>
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div ref={containerRef} style={{ position: 'relative' }}>
            <div
                ref={trackRef}
                style={{
                    display: 'flex',
                    width: `${storyPanels.length * 100}vw`,
                    willChange: 'transform',
                }}
            >
                {storyPanels.map((panel, i) => (
                    <div
                        key={i}
                        className="story-panel"
                        style={{
                            width: '100vw',
                            height: '100vh',
                            background: panel.bg,
                            color: panel.text,
                            flexShrink: 0,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: '0 10vw',
                            position: 'relative',
                            overflow: 'hidden'
                        }}
                    >
                        {/* Number Watermark */}
                        <div style={{
                            position: 'absolute',
                            top: '5%',
                            right: '5%',
                            fontFamily: 'var(--font-display)',
                            fontSize: '25vw',
                            opacity: 0.06,
                            pointerEvents: 'none',
                            lineHeight: 1
                        }}>
                            {panel.num}
                        </div>

                        <div className="max-w-4xl w-full">
                            <h2 className="panel-headline" style={{
                                fontFamily: 'var(--font-display)',
                                fontSize: 'clamp(3rem, 6vw, 6rem)',
                                marginBottom: '1.5rem',
                                lineHeight: 1,
                            }}>
                                {panel.headline}
                            </h2>
                            <div className="panel-body" style={{
                                fontFamily: 'var(--font-body)',
                                fontSize: 'clamp(1rem, 1.3vw, 1.125rem)',
                                maxWidth: '800px',
                                lineHeight: 1.6,
                                opacity: 0.9
                            }}>
                                {panel.body}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
