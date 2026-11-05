/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Cormorant", "Georgia", "serif"],
        sans: ["Montserrat", "system-ui", "sans-serif"],
      },
      colors: {
        background: "var(--color-background)",
        surface: "var(--color-surface)",
        "surface-elevated": "var(--color-surface-elevated)",
        primary: {
          DEFAULT: "var(--color-primary)",
          hover: "var(--color-primary-hover)",
          foreground: "var(--color-on-primary)",
        },
        secondary: {
          DEFAULT: "var(--color-secondary)",
          foreground: "var(--color-on-secondary)",
        },
        accent: {
          DEFAULT: "var(--color-accent)",
          foreground: "var(--color-on-accent)",
        },
        foreground: "var(--color-text-main)",
        muted: {
          DEFAULT: "var(--color-muted)",
          foreground: "var(--color-text-muted)",
        },
        border: "var(--color-border)",
        input: {
          DEFAULT: "var(--color-input-bg)",
          border: "var(--color-input-border)",
        },
        success: "var(--color-success)",
        warning: "var(--color-warning)",
        error: "var(--color-error)",
        overlay: "var(--color-overlay)",
        ring: "var(--color-focus-ring)",
      },
      boxShadow: {
        card: "var(--shadow-card)",
        elevated: "var(--shadow-elevated)",
      },
      borderRadius: {
        DEFAULT: "0.625rem",
        lg: "0.75rem",
        xl: "1rem",
      },
    },
  },
  plugins: [],
};
