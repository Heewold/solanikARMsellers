module.exports = {
  content: ['./templates/**/*.html','./**/templates/**/*.html'],
  theme: { extend: {} },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [{
      armtheme: {
        primary:'#4f46e5', secondary:'#475569', accent:'#22c55e',
        neutral:'#1f2937', 'base-100':'#ffffff',
        info:'#0ea5e9', success:'#16a34a', warning:'#f59e0b', error:'#e11d48'
      }
    }, 'light','dark']
  }
}
