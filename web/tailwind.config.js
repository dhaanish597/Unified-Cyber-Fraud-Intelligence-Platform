/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: '#070A10',
          surface: '#0F1420',
          panel: '#151C2C',
          border: '#1E293B',
          borderHover: '#334155',
          text: '#F3F4F6',
          muted: '#9CA3AF',
          dim: '#6B7280',
          primary: '#3B82F6',
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444',
          quantum: '#8B5CF6'
        }
      }
    },
  },
  plugins: [],
}

