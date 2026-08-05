const linkElements = document.querySelectorAll("[data-link]");

function copy(linkElement) {
  navigator.clipboard.writeText(linkElement.dataset.link).then(() => {
    const text = linkElement.textContent;

    linkElement.textContent = "Copied";

    setTimeout(() => {
      linkElement.textContent = text;
    }, 3000);
  });
}

linkElements.forEach((linkElement) => {
  linkElement.addEventListener("click", (event) => {
    copy(event.currentTarget);
  });
});
