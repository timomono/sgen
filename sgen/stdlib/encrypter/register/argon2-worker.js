import { hashPassword } from "./argon2.js";

self.addEventListener("error", (e) => {
    console.error("Global worker error:", e.message);
});

self.onmessage = async (e) => {
    if (e.data?.name === "hashPassword") {
        try {
            const result = await hashPassword(...(e.data.args ?? []));

            self.postMessage({
                name: "hashPassword",
                result,
            });
        } catch (err) {
            self.postMessage({
                name: "hashPassword",
                error: err.message || String(err),
            });
        }
    }
};