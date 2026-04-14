import { getFingerprint } from "./fingerprint.js";
import { createWebAuthn, getWebAuthn } from "./webauthn.js";
import { sha256 } from "./hash.js";

(() => {
    let webAuthn;
    let fingerprint;

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

    const registerFingerprint = () => {
        disableButtons();
        getFingerprint().then((res) => {
            fingerprint = res;
            enableButtons();
        }).catch(err => {
            alert("Fingerprint registration failed: " + err);
            enableButtons();
        });
    }

    const register = async () => {
        const codeElement = document.getElementById("authentication-code");
        const dialogOverlay = document.getElementById("dialog-overlay")

        const checkedMethods = [
            document.getElementById("method-password").checked ? "password" : null,
            document.getElementById("method-webauthn").checked ? "webauthn" : null,
            document.getElementById("method-button").checked ? "fingerprint" : null,
        ].filter(Boolean);

        if (checkedMethods.length === 0 || document.getElementById("username").value === "" || (
            (checkedMethods.includes("password") && !document.getElementById("password").value)
            || (checkedMethods.includes("webauthn") && !webAuthn)
            || (checkedMethods.includes("fingerprint") && !fingerprint)
        )) {
            alert("Enter missing value(s)");
            return;
        }

        const dataToHash = [
            checkedMethods.includes("password") ? await sha256(document.getElementById("password").value) : "",
            checkedMethods.includes("webauthn") ? await sha256(webAuthn) : "",
            checkedMethods.includes("fingerprint") ? await sha256(fingerprint) : "",
        ].join('');

        const code = await sha256(dataToHash);
        codeElement.innerText = code;
        dialogOverlay.classList.remove("hidden")
        // sha256()
    }

    document.getElementById("webauthn").addEventListener("click", registerWebAuthn)
    document.getElementById("fingerprint").addEventListener("click", registerFingerprint)
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
    toggle("method-button", "fingerprint-box");
})();