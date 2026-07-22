function focus(modalElement) {
  const input = modalElement.querySelector("[type=text]");

  input.focus();
}

const modalElement = document.querySelector("#modal");

modalElement.addEventListener("shown.bs.modal", (event) => {
  focus(event.currentTarget);
});

async function online() {
  const clientElements = document.querySelectorAll("[data-name]");

  if (clientElements.length === 0) {
    return;
  }

  let response = await fetch("/xray/online/");

  if (!response.ok) {
    return;
  }

  response = await response.json();

  const names = new Set(response.names);

  clientElements.forEach((clientElement) => {
    if (names.has(clientElement.dataset.name)) {
      clientElement.classList.add("border-primary");
    } else {
      clientElement.classList.remove("border-primary");
    }
  });
}

await online();

setInterval(async () => {
  await online();
}, 3000);
