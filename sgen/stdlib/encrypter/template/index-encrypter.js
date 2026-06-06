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

    const auth_spinner = document.getElementById("auth_spinner");

    auth_form.addEventListener("submit", (e) => {
        e.preventDefault()
        if (username_field.value.replace(" ", "") === "") {
            username_error.innerText = "The username is empty."
            return;
        }
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

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main)
} else {
    main()
}