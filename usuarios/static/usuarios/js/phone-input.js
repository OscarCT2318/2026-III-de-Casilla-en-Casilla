document.addEventListener("input", (event) => {
  const input = event.target;
  if (!(input instanceof HTMLInputElement) || !input.matches("[data-digits-only]")) {
    return;
  }

  const cursorPosition = input.selectionStart ?? input.value.length;
  const prefix = input.value.slice(0, cursorPosition).replace(/[^0-9]/g, "");
  const digitsOnly = input.value.replace(/[^0-9]/g, "");
  if (digitsOnly === input.value) {
    return;
  }

  input.value = digitsOnly;
  input.setSelectionRange(prefix.length, prefix.length);
});
