document.addEventListener("alpine:init", () => {
  Alpine.data('prediction', () => {
    return {
      show: false,
      predict: false,
      data: false,
      recommend: false,
      low: false,
      moderate: false,
      high: false,
      very_high: false,
      table_1: false,
      table_2: false,
      input: true,
      legend: false,
      tools: false,

    }
  })
})