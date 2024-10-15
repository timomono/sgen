// Minified version is in middleware.py
// alert("called")

async function decodeImages() {
    try {
        const src_list = []; // Dynamically update
        const div_files = {};
        // alert("domcontentloaded from " + src_list.length)
        for (const element of document.querySelectorAll("*[data-prot-src-id]:not(img)")) {
            /**@type {string} */
            const fromURL = src_list[element.dataset["protSrcId"]];
            const blob = (await (await fetch(fromURL)).blob());
            const slicedBlob = blob.slice(1, blob.size, blob.type);
            let blobUrl = URL.createObjectURL(slicedBlob) // Remove \xff
            blobUrl = fromURL.includes("#") ? blobUrl + "#" + fromURL.split("#").slice(-1)[0] : blobUrl
            element.addEventListener("load",
                () => URL.revokeObjectURL(blobUrl))
            if (element.src !== undefined) {
                element.src = blobUrl;
            } else if (element.getAttribute("xlink:href") !== undefined) {
                element.setAttribute("xlink:href", blobUrl);
            }
        }
        for (const element of document.querySelectorAll("img[data-prot-src-id]")) {
            // Context menu
            element.addEventListener("contextmenu", (e) => e.preventDefault())
            // Drag & drop
            element.addEventListener("mousedown", (e) => e.preventDefault())
            // Long press (smart phone)
            element.style["pointer-events"] = "none";

            // Overlay a transparent dummy image
            const dummy_img = document.createElement("img");
            dummy_img.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAAtJREFUGFdjYAACAAAFAAGq1chRAAAAAElFTkSuQmCC";

            const div_element = document.createElement("div");
            // Object.assign(div_element.style, {...element.style})
            for (const property of element.style) {
                div_element.style[property] = element.style[property];
            }
            // div_element.style.display = element.style.display;
            // div_element.style.width = element.style.width;
            div_element.style.position = "relative";
            dummy_img.style.position = "absolute";
            dummy_img.style.width = "100%";
            dummy_img.style.height = "100%";
            dummy_img.style.top = "0";
            dummy_img.style.bottom = "0";
            dummy_img.style.left = "0";
            dummy_img.style.right = "0";
            dummy_img.alt = "Dummy image";
            // Context menu
            dummy_img.addEventListener("contextmenu", (e) => e.preventDefault())
            // Drag & drop
            dummy_img.addEventListener("mousedown", (e) => e.preventDefault())
            element.parentNode.insertBefore(div_element, element);
            // 
            for (const part_img_src of div_files[src_list[element.dataset["protSrcId"]]]) {
                const part_img = document.createElement("img")

                const fromURL = part_img_src;
                const blob = (await (await fetch(fromURL)).blob());
                const slicedBlob = blob.slice(1, blob.size, blob.type);
                let blobUrl = URL.createObjectURL(slicedBlob) // Remove \xff
                blobUrl = fromURL.includes("#") ? blobUrl + "#" + fromURL.split("#").slice(-1)[0] : blobUrl
                part_img.addEventListener("load",
                    () => URL.revokeObjectURL(blobUrl))
                if (part_img.src !== undefined) {
                    part_img.src = blobUrl;
                } else if (element.getAttribute("xlink:href") !== undefined) {
                    element.setAttribute("xlink:href", blobUrl);
                }
                part_img.style.position = "absolute";
                part_img.style.width = "100%";
                part_img.style.height = "100%";
                part_img.style.top = "0";
                part_img.style.bottom = "0";
                part_img.style.left = "0";
                part_img.style.right = "0";
                part_img.alt = element.alt;
                div_element.append(part_img);
            }
            element.remove()
            div_element.append(dummy_img)
        }
    } catch (e) {
        console.error(e)
    }
}
if (document.readyState === 'loading') {
    document.addEventListener("DOMContentLoaded", (e) => decodeImages())
} else {
    decodeImages()
}