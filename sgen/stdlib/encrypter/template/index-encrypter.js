"use strict";
import { getFingerprint } from "./_encrypter/components/fingerprint.js";
import { createWebAuthn, getWebAuthn } from "./_encrypter/components/webauthn.js";
import { sha256 } from "./_encrypter/components/hash.js";
import { hashPasswordWithWorker } from "./_encrypter/components/argon2-worker-caller.js";
import { hashPassword } from "../_encrypter/components/argon2.js";

const byteToMethods = (byte) => {
    const methodsMap = {
        password: 1 << 0, // 00000001
        webAuthn: 1 << 1, // 00000010
        fingerprint: 1 << 2, // 00000100
    };

    const methods = [];
    for (const method of Object.keys(methodsMap)) {
        const mask = methodsMap[method];
        if ((byte & mask) !== 0) { //The method is included
            methods.push(method)
        }
    }
    return methods;
}

const main = () => {
    const auth_page = document.getElementById("auth_page");
    const password_page = document.getElementById("password_page")
    const username_field = document.getElementById("username");
    const username_error = document.getElementById("username_error");

    const password_field = document.getElementById("password");
    const password_error = document.getElementById("password_error");

    const next_btn = document.getElementById("next_btn")
    const auth_btn = document.getElementById("auth_btn")

    const auth_form = document.getElementById("auth_form");
    const password_form = document.getElementById("password_form");

    const next_spinner = document.getElementById("next_spinner");
    const auth_spinner = document.getElementById("auth_spinner");

    auth_form.addEventListener("submit", async (e) => {
        e.preventDefault()
        if (username_field.value.replace(" ", "") === "") {
            username_error.innerText = "The username is empty."
            return;
        }

        // Spinner
        next_btn.disabled = true;
        next_spinner.classList.remove("hidden")

        // Get the auth method for this username
        let fetched_data;
        try {
            fetched_data = await fetch("/keys");
        } catch (e) {
            username_error.innerText = `Fetch failed: ${e}`
            next_btn.disabled = false;
            next_spinner.classList.add("hidden")
            return;
        }
        if (!fetched_data.ok) {
            username_error.innerText = `HTTP Error: ${fetched_data.status} ${fetched_data.statusText}`
            next_btn.disabled = false;
            next_spinner.classList.add("hidden")
            return;
        }
        const raw_keys = await fetched_data.text();
        const keys = raw_keys.split("\n");

        const match_keys = [];
        for (const s of keys) {
            if (s === "") continue;
            const username_salt = s.slice(1, 65);
            const username_hash = s.slice(65, 129);
            const username_salt_bytes = String.fromCharCode(...new Uint8Array(username_salt.match(/.{1,2}/g).map(b => parseInt(b, 16))));
            const computed_hash = await sha256(username_salt_bytes + username_field.value);
            if (computed_hash === username_hash) {
                match_keys.push(s);
            }
        }

        if (match_keys.length === 0) {
            username_error.innerText = "The user not found."
            next_btn.disabled = false;
            next_spinner.classList.add("hidden")
            return;
        }
        if (match_keys.length > 1) {
            username_error.innerText = "Multiple users with same username"
            next_btn.disabled = false;
            next_spinner.classList.add("hidden")
            return;
        }

        const encrypted_key = match_keys[0];
        console.log(encrypted_key)
        const auth_method = byteToMethods(parseInt(encrypted_key[0], 16));
        window.auth_method = auth_method;

        console.log(auth_method)
        if (auth_method.includes("password")) {
            // Store for password page
            window.encrypted_key = encrypted_key;
            window.webAuthn = null;
            window.fingerprint = null;

            if (auth_method.includes("webAuthn")) {
                window.webAuthn = await getWebAuthn();
            }
            if (auth_method.includes("fingerprint")) {
                window.fingerprint = await getFingerprint();
            }

            // Next page
            auth_page.classList.add("page_hidden")
            password_page.classList.remove("page_hidden");
            history.pushState("", "", "")
        } else {
            // WebAuthn/Fingerprint only - verify immediately
            let webAuthn;
            if (auth_method.includes("webAuthn")) {
                webAuthn = await getWebAuthn();
            }
            let fingerprint;
            if (auth_method.includes("fingerprint")) {
                fingerprint = await getFingerprint();
            }

            const key_salt_hex = encrypted_key.slice(129, 193); // 32 bytes as hex (64 chars)
            const key_hash = encrypted_key.slice(193); // rest is the hash
            const username_salt = encrypted_key.slice(1, 65);
            const username_salt_bytes = String.fromCharCode(...new Uint8Array(username_salt.match(/.{1,2}/g).map(b => parseInt(b, 16))));

            const dataToHash = [
                await sha256(username_salt_bytes + username_field.value),
                "",
                auth_method.includes("webAuthn") ? await sha256(JSON.stringify(webAuthn)) : "",
                auth_method.includes("fingerprint") ? await sha256(JSON.stringify(fingerprint)) : "",
            ].join('');

            const computed_hash = await sha256(await hashPasswordWithWorker(dataToHash));

        }
    })

    password_form.addEventListener("submit", async (e) => {
        e.preventDefault()
        if (password_field.value.replace(" ", "") === "") {
            password_error.innerText = "The password is empty."
            return;
        }

        auth_btn.disabled = true;
        auth_spinner.classList.remove("hidden")

        try {
            const encrypted_key = window.encrypted_key;
            const auth_method = window.auth_method;
            const username_salt = encrypted_key.slice(1, 65);
            const key_salt = new Uint8Array(encrypted_key.slice(129, 161).match(/.{1,2}/g).map(b => parseInt(b, 16)));
            const encrypted_raw_key = encrypted_key.slice(161);

            const username_salt_bytes = String.fromCharCode(...new Uint8Array(username_salt.match(/.{1,2}/g).map(b => parseInt(b, 16))));

            const dataToHash = [
                await sha256(username_salt_bytes + username_field.value),
                await sha256(password_field.value),
                auth_method.includes("webAuthn") ? await sha256(JSON.stringify(window.webAuthn)) : "",
                auth_method.includes("fingerprint") ? await sha256(JSON.stringify(window.fingerprint)) : "",
            ].join('');

            const computed_hash = (await hashPasswordWithWorker(
                dataToHash,
                key_salt
            )).key;

            // Decrypt the encrypted key
            const encrypted_data_hex = encrypted_key.slice(195);
            const iv = new Uint8Array(encrypted_data_hex.slice(0, 24).match(/.{1,2}/g).map(b => parseInt(b, 16)));
            const ciphertext = new Uint8Array(encrypted_data_hex.slice(24).match(/.{1,2}/g).map(b => parseInt(b, 16)));


            const key = await crypto.subtle.importKey(
                "raw",
                computed_hash,
                { name: "AES-GCM" },
                false,
                ["decrypt"]
            );

            try {
                console.log(Array.from(iv)
                    .map(b => b.toString(16).padStart(2, '0'))
                    .join(''), Array.from(computed_hash)
                        .map(b => b.toString(16).padStart(2, '0'))
                        .join(''), Array.from(ciphertext)
                            .map(b => b.toString(16).padStart(2, '0'))
                            .join(''), encrypted_data_hex)
                const decrypted = await crypto.subtle.decrypt(
                    { name: "AES-GCM", iv: iv },
                    key,
                    ciphertext
                );
                console.log(decrypted)
                const decrypted_key = new TextDecoder().decode(decrypted);
                password_error.innerText = "Login successful!";
                password_error.style.color = "#4a90e2";
                // TODO: use decrypted_key for further actions
            } catch (decryptErr) {
                console.error(decryptErr)
                password_error.innerText = "Invalid password";
                password_error.style.color = "#e74c3c";
            }
        } catch (err) {
            password_error.innerText = `Error: ${err.message}`;
            password_error.style.color = "#e74c3c";
        } finally {
            auth_btn.disabled = false;
            auth_spinner.classList.add("hidden")
        }
    })
}

(() => {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", main)
    } else {
        main()
    }
})();