const modalElement = document.querySelector("#modal");

function focus(modalElement) {
  const input = modalElement.querySelector("[type=text]");

  input.focus();
}

modalElement.addEventListener("shown.bs.modal", (event) => {
  focus(event.currentTarget);
});
