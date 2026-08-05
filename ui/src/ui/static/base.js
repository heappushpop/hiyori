const toastElements = document.querySelectorAll(".toast");

toastElements.forEach((toastElement) => {
  bootstrap.Toast.getOrCreateInstance(toastElement).show();
});
