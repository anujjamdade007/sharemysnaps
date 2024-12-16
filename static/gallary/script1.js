const imageWrapper = document.querySelector(".images");
const searchInput = document.querySelector(".search input");
const loadMoreBtn = document.querySelector(".gallery .load-more");
const lightbox = document.querySelector(".lightbox");
const downloadImgBtn = lightbox.querySelector(".uil-import");
const closeImgBtn = lightbox.querySelector(".close-icon");


const downloadImg = (imgUrl) => {
    // Create a notification element for "Download started"
    const downloadNotification = document.createElement("div");
    downloadNotification.textContent = "Download started...";
    downloadNotification.style.position = "fixed";
    downloadNotification.style.top = "20px";
    downloadNotification.style.left = "50%";
    downloadNotification.style.transform = "translateX(-50%)";
    downloadNotification.style.backgroundColor = "#4CAF50";
    downloadNotification.style.color = "#fff";
    downloadNotification.style.padding = "10px 20px";
    downloadNotification.style.borderRadius = "5px";
    downloadNotification.style.fontSize = "14px";
    downloadNotification.style.zIndex = "9999";
    document.body.appendChild(downloadNotification);

    // Make the notification disappear after 2 seconds
    setTimeout(() => {
        downloadNotification.style.opacity = "0";
        setTimeout(() => {
            downloadNotification.remove(); // Remove the element after it fades out
        }, 500); // Delay for fading effect
    }, 2000);

    // Fetch the image as a blob
    fetch(imgUrl)
        .then(res => {
            if (!res.ok) {
                throw new Error("Failed to fetch image");
            }
            return res.blob(); // Get the image blob
        })
        .then(blob => {
            // Create a new object URL for the blob
            const a = document.createElement("a");

            // Get the file extension from the URL (e.g., .jpg, .png, etc.)
            const fileExtension = imgUrl.split('.').pop().split('?')[0];
            
            // If the extension is not in the URL, use the MIME type from the response
            if (!fileExtension || fileExtension === imgUrl) {
                const contentType = blob.type.split('/')[1];
                a.download = `image.${contentType}`; // Default to content-type extension (jpg, png, etc.)
            } else {
                a.download = `image.${fileExtension}`; // Use the extension from the URL
            }

            // Create a download link and trigger the download
            a.href = URL.createObjectURL(blob);
            a.click();
        })
        .catch(() => {
            alert("Failed to download image!");
        });
}


const showLightbox = (name, img) => {
    // Showing lightbox and setting img source, name and button attribute
    lightbox.querySelector("img").src = img;
    lightbox.querySelector("span").innerText = name;
    downloadImgBtn.setAttribute("data-img", img);
    lightbox.classList.add("show");
    document.body.style.overflow = "hidden";
}

const hideLightbox = () => {
    // console.log("Lightbox hide triggered!"); // Debug log
    lightbox.classList.remove("show");
    document.body.style.overflow = "auto";
  }






closeImgBtn.addEventListener("click", hideLightbox);
downloadImgBtn.addEventListener("click", (e) => downloadImg(e.target.dataset.img));