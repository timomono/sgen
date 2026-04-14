import { getFingerprint } from "./fingerprint.js";
import { createWebAuthn, getWebAuthn } from "./webauthn.js";
import { sha256 } from "./hash.js";
import { hashPasswordWithWorker } from "./argon2-worker-caller.js";
import { hashPassword } from "./argon2.js"; // remove later

const generateUsername = () => "user" + Math.floor(Math.random() * 10000).toString().padStart(4, "0");

(() => {
    let webAuthn;
    let fingerprint;

    const methodsToByte = (methods) => {
        const methodsMap = {
            password: 1 << 0, // 00000001
            webAuthn: 1 << 1, // 00000010
            fingerprint: 1 << 2, // 00000100
        };

        let state = 0;

        for (const method of methods) {
            state |= methodsMap[method];
        }
        return state;
    }

    const disableButtons = () => {
        for (const btn of document.getElementsByTagName("button")) {
            btn.disabled = true;
        }
    }

    const enableButtons = () => {
        for (const btn of document.getElementsByTagName("button")) {
            btn.disabled = false;
        }
    }

    const registerWebAuthn = () => {
        disableButtons();
        createWebAuthn(document.getElementById("username").value).then(async () => {
            const key = await getWebAuthn();
            webAuthn = key;
            enableButtons();
        }).catch(err => {
            alert("WebAuthn registration failed: " + err);
            enableButtons();
        });
    }

    const register = async () => {
        disableButtons();
        const codeElement = document.getElementById("authentication-code");
        const dialogOverlay = document.getElementById("dialog-overlay")
        const spinner = document.querySelector(".spinner");
        spinner.classList.remove("hidden");

        const checkedMethods = [
            document.getElementById("method-password").checked ? "password" : null,
            document.getElementById("method-webauthn").checked ? "webauthn" : null,
            document.getElementById("method-button").checked ? "fingerprint" : null,
        ].filter(Boolean);

        if (checkedMethods.length === 0 || document.getElementById("username").value === "" || (
            (checkedMethods.includes("password") && !document.getElementById("password").value)
            || (checkedMethods.includes("webauthn") && !webAuthn)
        )) {
            alert("Enter missing value(s)");
            enableButtons();
            spinner.classList.add("hidden");
            return;
        }

        if (checkedMethods.includes("fingerprint")) {
            fingerprint = await getFingerprint();
        }

        const dataToHash = [
            document.getElementById("username").value,
            checkedMethods.includes("password") ? await sha256(document.getElementById("password").value) : "",
            checkedMethods.includes("webauthn") ? await sha256(webAuthn) : "",
            checkedMethods.includes("fingerprint") ? await sha256(fingerprint) : "",
        ].join('');

        const code = methodsToByte(checkedMethods) + await sha256(
            await hashPasswordWithWorker(dataToHash)
        ); // Increase the cost to try the password like PoW
        codeElement.innerText = code;

        enableButtons();
        dialogOverlay.classList.remove("hidden")
        spinner.classList.add("hidden");
        // sha256()
    }

    document.getElementById("webauthn").addEventListener("click", registerWebAuthn)
    document.getElementById("register").addEventListener("click", register)

    const toggle = (checkboxId, boxId) => {
        const checkbox = document.getElementById(checkboxId);
        const box = document.getElementById(boxId);

        checkbox.addEventListener("change", () => {
            box.classList.toggle("hidden", !checkbox.checked);
        });
    };

    toggle("method-password", "password-box");
    toggle("method-webauthn", "webauthn-box");

    // Set initial username
    document.getElementById("username").value = generateUsername();
})();