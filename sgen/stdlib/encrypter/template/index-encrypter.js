"use strict";
import { getFingerprint } from "./_encrypter/components/fingerprint.js";
import { createWebAuthn, getWebAuthn } from "./_encrypter/components/webauthn.js";
import { sha256 } from "./_encrypter/components/hash.js";
import { hashPasswordWithWorker } from "./_encrypter/components/argon2-worker-caller.js";
// import { hashPassword } from "../_encrypter/components/argon2.js";

const byteToMethods = (byte) => {
    const methodsMap = {
        password: 1 << 0, // 00000001
        webAuthn: 1 << 1, // 00000010
        fingerprint: 1 << 2, // 00000100
    };

    const methods = [];
    for (const method of Object.keys(methodsMap)) {
        const mask = methodsMap[method];
        if (methods & mask !== 0) { //The method is included
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
            return;
        }
        if (!fetched_data.ok) {
            username_error.innerText = `HTTP Error: ${fetched_data.status} ${fetched_data.statusText}`
            return;
        }
        const raw_keys = await fetched_data.text();
        const keys = raw_keys.split("\n");
        const match_keys = keys.filter(s => {
            const username_hash = s.slice(1, 65);
            if (sha256(username_field.value) === username_hash) {
                return true
            }
            return false;
        })

        if (match_keys.length === 0) {
            username_error.innerText = "The user not found."
            return;
        }
        if (match_keys.length > 1) {
            username_error.innerText = "Multiple users with same username"
            return;
        }

        const encrypted_key = match_keys[0];
        const auth_method = byteToMethods(parseInt(encrypted_key[0], 16));

        // Next page
        auth_page.classList.add("hidden")
        password_page.classList.remove("hidden");
        history.pushState("", "", "")
    })

    password_form.addEventListener("submit", (e) => {
        e.preventDefault()
        if (password_field.value.replace(" ", "") === "") {
            password_error.innerText = "The password is empty."
            return;
        }

        auth_btn.disabled = true;
        auth_spinner.classList.remove("hidden")
        // indexedDB.open("session").transaction("sessionKey", "")
    })
}

(() => {
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", main)
    } else {
        main()
    }
})();