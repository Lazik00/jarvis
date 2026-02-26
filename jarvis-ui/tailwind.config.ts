import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#07090f',
        panel: 'rgba(17, 24, 39, 0.55)',
        neon: '#27b6ff',
        success: '#37e6a4',
      },
      boxShadow: {
        glow: '0 0 20px rgba(39, 182, 255, 0.45)',
        purple: '0 0 20px rgba(155, 109, 255, 0.45)',
        success: '0 0 20px rgba(55, 230, 164, 0.45)',
      },
      animation: {
        pulseRing: 'pulseRing 1.8s ease-out infinite',
        waveform: 'waveform 1.2s ease-in-out infinite',
        fadeIn: 'fadeIn .3s ease-out',
      },
      keyframes: {
        pulseRing: {
          '0%': { transform: 'scale(0.85)', opacity: '.9' },
          '100%': { transform: 'scale(1.25)', opacity: '0' },
        },
        waveform: {
          '0%, 100%': { transform: 'scaleY(0.4)' },
          '50%': { transform: 'scaleY(1)' },
        },
        fadeIn: {
          from: { opacity: 0, transform: 'translateY(6px)' },
          to: { opacity: 1, transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
