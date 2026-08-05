async function online() {
  const onlineElements = document.querySelectorAll("[data-name]");

  if (onlineElements.length === 0) {
    return;
  }

  let response = await fetch("/xray/online/");

  if (!response.ok) {
    return;
  }

  response = await response.json();

  const names = new Set(response.names);

  onlineElements.forEach((onlineElement) => {
    if (names.has(onlineElement.dataset.name)) {
      onlineElement.classList.remove("d-none");
    } else {
      onlineElement.classList.add("d-none");
    }
  });
}

await online();

setInterval(async () => {
  await online();
}, 3000);
