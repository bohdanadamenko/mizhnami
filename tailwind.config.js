/** Збірка: npx tailwindcss@3 -c tailwind.config.js -i tailwind/input.css -o main/static/main/css/tailwind.css --minify */
module.exports = {
  content: ['./main/templates/**/*.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
        serif: ['"Cormorant Garamond"', 'serif'],
      },
      colors: {
        beige: { 50: '#FFFDF9', 100: '#FAF8F2', 200: '#F3EFE4', 300: '#E6DFCE' },
        lime: {
          50: '#F7FEE7', 100: '#ECFCCB', 300: '#BEF264', 400: '#A3E635',
          500: '#84CC16', 600: '#65A30D', 700: '#4D7C0F', 900: '#1E2916',
        },
      },
    },
  },
};
