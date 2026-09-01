async function request(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || "Request failed");
  }
  return response;
}

document.querySelector("#add-service-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  try {
    await request("/api/services", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: data.get("name"), url: data.get("url") }),
    });
    window.location.reload();
  } catch (error) {
    window.alert(error.message);
  }
});

async function checkService(id) {
  try {
    await request(`/api/services/${id}/check`, { method: "POST" });
    window.location.reload();
  } catch (error) {
    window.alert(error.message);
  }
}

async function checkAll() {
  try {
    await request("/api/services/check-all", { method: "POST" });
    window.location.reload();
  } catch (error) {
    window.alert(error.message);
  }
}

async function deleteService(id) {
  if (!window.confirm("Delete this service and its history?")) return;
  try {
    await request(`/api/services/${id}`, { method: "DELETE" });
    window.location.reload();
  } catch (error) {
    window.alert(error.message);
  }
}
