// Configure MathJax settings by assigning to window.MathJax
window.MathJax = {
  // TeX input processor configuration
  tex: {
    // Define delimiters for inline math expressions:
    inlineMath: [
      ["$", "$"],    // $...$ for inline math
      ["\\(", "\\)"] // \(...\) alternative syntax
    ],
    // Define delimiters for display (block) math expressions:
    displayMath: [
      ["$$", "$$"],  // $$...$$ for block math
      ["\\[", "\\]"] // \[...\] alternative syntax
    ]
  },
  // General processing options
  options: {
    // HTML tags that MathJax should skip/ignore
    skipHtmlTags: ["script", "noscript", "style", "textarea", "pre", "code"],
    // CSS class that tells MathJax to ignore elements
    ignoreHtmlClass: "tex2jax_ignore",
    // CSS class that tells MathJax to explicitly process elements
    processHtmlClass: "tex2jax_process",
  }
};

// Export the MathJax configuration (though it's already globally available)
export default window.MathJax;
