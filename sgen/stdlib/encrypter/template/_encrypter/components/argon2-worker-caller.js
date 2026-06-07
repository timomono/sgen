export function hashPasswordWithWorker(password, salt) {
    return new Promise((resolve, reject) => {
        if (window.Worker) {
            const worker = new Worker(
                new URL("argon2-worker.js", import.meta.url),
                { type: "module" }
            );

            worker.postMessage({
                name: "hashPassword",
                args: [password, salt],
            });

            worker.onmessage = (m) => {
                if (m.data?.name === "hashPassword") {
                    worker.terminate();

                    if (m.data.error) {
                        reject(new Error(m.data.error));
                    } else {
                        resolve(m.data.result);
                    }
                }
            };

            worker.onerror = (e) => {
                worker.terminate();
                reject(e);
            };

            worker.onmessageerror = (e) => {
                worker.terminate();
                reject(e);
            };
        } else {
            hashPassword(password)
                .then(resolve)
                .catch(reject);
        }
    });
}