const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const uploadLoader = document.getElementById("uploadLoader");

dropZone.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (e) => handleFileUpload(e.target.files[0]));

dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("active"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("active"));
dropZone.addEventListener("drop", (e) => {
    e.preventDefault(); dropZone.classList.remove("active");
    if (e.dataTransfer.files.length > 0) handleFileUpload(e.dataTransfer.files[0]);
});

async function handleFileUpload(file) {
    if (!file) return;
    dropZone.classList.add("hidden");
    uploadLoader.classList.remove("hidden");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload/", { method: "POST", body: formData });
        if (!response.ok) throw new Error("Upload failed");
        const data = await response.json();
        sessionStorage.setItem("file_path", data.file_path);
        sessionStorage.setItem("data_profile", JSON.stringify(data.data_profile));
        window.location.href = "/dashboard";
    } catch (error) {
        alert("Error: " + error.message);
        uploadLoader.classList.add("hidden");
        dropZone.classList.remove("hidden");
    }
}