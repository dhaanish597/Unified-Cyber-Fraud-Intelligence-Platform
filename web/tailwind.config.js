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
          bg: '#0B0F19',
          panel: '#151A25',
          border: '#2A303C',
          text: '#9CA3AF',
          primary: '#3B82F6',
          success: '#10B981',
          warning: '#F59E0B',
          danger: '#EF4444'
        }
      }
    },
  },
  plugins: [],
}
