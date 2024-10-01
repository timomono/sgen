
// Make window.getEventListeners available
function makeGetEventListenersAvailable(targetClass) {
    const eventListeners = [];
    const originalAddEventListener = targetClass.prototype.addEventListener;
    const originalRemoveEventListener = targetClass.prototype.removeEventListener;
    targetClass.prototype.addEventListener = function (type, listener, options) {
        eventListeners.push({target: this, type, listener, options});
        originalAddEventListener.call(this, type, listener, options);
    };
    targetClass.prototype.removeEventListener = function (type, listener, options) {
        console.log("removing event listener: " + type)
        find: {
            for (const i in eventListeners) {
                const eventListener = eventListeners[i]
                if (eventListener.target === this && eventListener.type === type && eventListener.listener === listener) {
                    eventListeners.splice(i, 1);
                    break find;
                }
            }
            console.error("Couldn't found event listener.")
            console.error({target: this, type, listener, options})
        }
        originalRemoveEventListener.call(this, type, listener, options);
    };
    // @ts-ignore
    targetClass.getEventListeners = function () {
        return eventListeners;
    };
    window.getEventListeners = function () {
        return eventListeners;
    };
}

makeGetEventListenersAvailable(Document)
// makeGetEventListenersAvailable(Window)
// makeGetEventListenersAvailable(EventTarget)


function addLinkEventHandler() {
    document.addEventListener("DOMContentLoaded", (event) => {
        document.documentElement.classList.remove("spa_loading");
        addToLinkTag()
    })
}
addLinkEventHandler()
window.addEventListener("popstate", async (event) => {
    history.replaceState({}, "", location.href);
    transition(location.href);
});
async function addToLinkTag() {
    const links = document.getElementsByTagName("a");
    for (const link of links) {
        link.addEventListener(
            "click",
            async function (e) {
                e.preventDefault();
                history.pushState({}, "", link.href);

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
        const sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));
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

        for (const listener of window.getEventListeners()) {
            console.log(listener["type"])
            console.log(listener["listener"])
            await listener["target"].removeEventListener(listener["type"], listener["listener"], listener["options"])
        }
        console.log("removed")
        // console.log("Waiting...")
        // await sleep("3000")
        // console.log("Removed!")

        const parser = new DOMParser();
        const doc = parser.parseFromString(text, 'text/html');

        // document.replaceChild(
        //     document.adoptNode(doc.documentElement),
        //     document.documentElement
        // );

        let observer = new MutationObserver((mutationsList, observer) => {
            for (let mutation of mutationsList) {
                if (mutation.type === "childList") {
                    console.log("good! loaded!")
                    observer.disconnect()
                    runAfterContentLoaded();
                    return
                }
            }
        });
        let config = {childList: true, subtree: true};

        // /**
        //  * @returns {object[]}
        //  */
        // const window.getEventListeners;


        observer.observe(document.documentElement, config);

        document.documentElement.innerHTML = doc.documentElement.innerHTML;
        // document.replaceChild(
        //     document.adoptNode(doc.documentElement),
        //     document.documentElement
        // );

        addToLinkTag()
        async function runAfterContentLoaded() {
            document.dispatchEvent(new Event("DOMContentLoaded"))
            console.log(document.title)
            const scripts = doc.querySelectorAll('script');
            console.log(scripts)
            scripts.forEach(oldScript => {
                const newScript = document.createElement('script');
                if (oldScript.textContent != "") {
                    newScript.textContent = oldScript.textContent;
                }
                if (oldScript.src != "") {
                    newScript.src = oldScript.src;
                }
                document.head.appendChild(newScript);
            });
        }

    } catch (error) {
        console.error(error.message);
    } finally {
        document.dispatchEvent(new Event("spa_loaded"));
        document.documentElement.classList.remove("spa_loading");
    }
}
window.transition = transition;