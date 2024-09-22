function addLinkEventHandler() {
    document.addEventListener("DOMContentLoaded", (event) => {
        document.documentElement.classList.remove("spa_loading");
        addToLinkTag()
    })
}
addLinkEventHandler()
window.addEventListener("popstate", async (event) => {
    await history.replaceState({}, "", location.href);
    transition(location.href);
});
async function addToLinkTag() {
    const links = document.getElementsByTagName("a");
    for (const link of links) {
        link.addEventListener(
            "click",
            async function (e) {
                e.preventDefault();
                await history.pushState({}, "", link.href);

                const url = link.href;
                // console.log(e.target)
                // console.log(url)
                transition(url);
            },
        );
    }
}
// Non-html link will be broken (like image file)
async function transition(url) {
    try {
        document.dispatchEvent(new Event("spa_loading"));
        document.documentElement.classList.add("spa_loading");
        const response = await fetch(url);
        if (!response.ok) {
            if (response.status == 404) {
                console.log("404 Error. ")
            }
            console.error(`Status not ok: ${response.status} URL: ${url}`);
        }
        const text = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');

        // Run scripts
        const scripts = doc.querySelectorAll('script');
        doc.documentElement.classList.add("spa_loading");
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            newScript.textContent = oldScript.textContent;
            document.head.appendChild(newScript);
        });

        // document.replaceChild(
        //     document.adoptNode(doc.documentElement),
        //     document.documentElement
        // );
        document.documentElement.innerHTML = doc.documentElement.innerHTML;
        addToLinkTag()
    } catch (error) {
        console.error(error.message);
    } finally {
        document.dispatchEvent(new Event("spa_loaded"));
        document.documentElement.classList.remove("spa_loading");
    }
}
window.transition = transition;