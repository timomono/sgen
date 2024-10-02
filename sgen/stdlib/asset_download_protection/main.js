// alert("called")
document.addEventListener("DOMContentLoaded", async (event) => {
    const src_list = [];
    // alert("domcontentloaded from " + src_list.length)
    for (const element of document.querySelectorAll("*[data-prot-src-id]")) {
        /**@type {string} */
        const fromURL = src_list[element.dataset["protSrcId"]];
        const blob = (await (await fetch(fromURL)).blob());
        const slicedBlob = blob.slice(1, blob.size, blob.type);
        const blobUrl = URL.createObjectURL(slicedBlob) // Remove \xff
        element.src = blobUrl;
        element.addEventListener("load",
            () => URL.revokeObjectURL(blobUrl))

        if (element.tagName.toLowerCase() == "img") {
            // Context menu
            element.addEventListener("contextmenu", (e) => e.preventDefault())
            // Drag & drop
            element.addEventListener("mousedown", (e) => e.preventDefault())
            // Overlay a transparent dummy image
            const parent = element.parentElement;
            const dummy_img = document.createElement("img");
            dummy_img.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC";

            const div_element = document.createElement("div");
            div_element.style.position = "relative";
            dummy_img.style.position = "absolute";
            dummy_img.style.width = "100%";
            dummy_img.style.height = "100%";
            dummy_img.style.top = "0";
            dummy_img.style.bottom = "0";
            dummy_img.style.left = "0";
            dummy_img.style.right = "0";
            // Context menu
            dummy_img.addEventListener("contextmenu", (e) => e.preventDefault())
            // Drag & drop
            dummy_img.addEventListener("mousedown", (e) => e.preventDefault())
            parent.append(div_element);
            div_element.append(element)
            div_element.append(dummy_img)
        }
    }
})