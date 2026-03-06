import { motion } from 'framer-motion';

const words = ['LUMIN', '⚡', 'AI', 'INTELLIGENCE', 'PLATFORM'];

export const HeroSection = () => {
    return (
        <section className="relative min-h-[100vh] w-full overflow-hidden flex flex-col items-center justify-center pt-24" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
            {/* Background radial gold glow */}
            <motion.div
                animate={{ scale: [1, 1.08, 1] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                style={{
                    position: 'absolute',
                    width: '80vw',
                    height: '80vw',
                    bottom: '-30%',
                    background: 'radial-gradient(ellipse 60% 50% at 50% 70%, rgba(212,144,10,0.12) 0%, transparent 70%)',
                    pointerEvents: 'none',
                }}
            />

            {/* Diagonal SVG polygon shapes bottom-right */}
            <svg viewBox="0 0 400 600" style={{ position: 'absolute', bottom: -100, right: -100, width: '400px', opacity: 0.15, pointerEvents: 'none' }}>
                <polygon points="400,0 400,600 80,600" fill="var(--color-brand-muted)" />
            </svg>

            {/* Floating Particles */}
            {Array.from({ length: 30 }).map((_, i) => (
                <motion.div
                    key={i}
                    initial={{ y: 0, opacity: 0.4 }}
                    animate={{ y: [0, -120], opacity: [0.4, 0] }}
                    transition={{
                        duration: 3 + Math.random() * 4,
                        repeat: Infinity,
                        delay: Math.random() * 4,
                        ease: "linear"
                    }}
                    style={{
                        position: 'absolute',
                        left: `${Math.random() * 100}%`,
                        top: `${Math.random() * 100}%`,
                        width: `${2 + Math.random() * 2}px`,
                        height: `${2 + Math.random() * 2}px`,
                        borderRadius: '50%',
                        background: 'var(--color-brand-light)',
                        pointerEvents: 'none',
                    }}
                />
            ))}

            {/* Hero Title */}
            <div className="relative z-10 text-center max-w-5xl px-4 flex flex-col items-center">
                <div className="flex flex-wrap justify-center items-center gap-x-4 gap-y-2 md:gap-x-6">
                    {words.slice(0, 3).map((w, i) => (
                        <motion.span
                            key={i}
                            initial={{ opacity: 0, y: 60 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.08, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
                            style={{
                                fontFamily: 'var(--font-display)',
                                fontSize: 'var(--text-hero)',
                                color: w === '⚡' ? 'var(--color-brand-accent)' : 'var(--color-text-primary)',
                                lineHeight: 1,
                            }}
                        >
                            {w}
                        </motion.span>
                    ))}
                </div>
                <motion.div
                    initial={{ opacity: 0, y: 60 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 3 * 0.08, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
                    style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: 'var(--text-hero)',
                        WebkitTextStroke: '2px var(--color-brand-primary)',
                        color: 'transparent',
                        lineHeight: 1,
                        marginTop: '-0.1em'
                    }}
                >
                    {words[3]}
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 60 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 4 * 0.08, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
                    style={{
                        fontFamily: 'var(--font-display)',
                        fontSize: 'var(--text-hero)',
                        color: 'var(--color-brand-primary)',
                        lineHeight: 1,
                        marginTop: '-0.1em'
                    }}
                >
                    {words[4]}
                </motion.div>
            </div>

            {/* Glassmorphism Stat Cards */}
            <div className="relative w-full max-w-6xl mx-auto h-[200px] mt-8 md:absolute md:inset-0 md:h-full md:mt-0 pointer-events-none flex flex-col md:block px-4 gap-4">
                {[
                    { text: "⚡ 17% of all faults", pos: { top: '25%', left: '5%' } },
                    { text: "🔴 $4.6B lost in 2023", pos: { bottom: '20%', left: '50%', x: '-50%' } },
                    { text: "📉 80 days avg downtime", pos: { top: '35%', right: '4%' } }
                ].map((item, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.94 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 0.6 + i * 0.15, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
                        className="md:absolute self-center md:self-auto w-full md:w-auto"
                        style={{ ...item.pos }}
                    >
                        <motion.div
                            animate={{ y: [0, -15, 0] }}
                            transition={{ duration: 4 + i * 0.5, repeat: Infinity, ease: 'easeInOut' }}
                            style={{
                                backdropFilter: 'blur(16px) saturate(160%)',
                                background: 'rgba(255, 248, 231, 0.6)',
                                border: '1px solid rgba(212, 144, 10, 0.25)',
                                boxShadow: '0 8px 32px rgba(212, 144, 10, 0.12)',
                                borderRadius: 'var(--radius-lg)',
                                padding: '16px 24px',
                                fontFamily: 'var(--font-heading)',
                                fontWeight: 600,
                                fontSize: '1rem',
                                color: 'var(--color-text-primary)'
                            }}
                        >
                            {item.text}
                        </motion.div>
                    </motion.div>
                ))}
            </div>
        </section>
    );
};
