import sodium from "https://cdn.jsdelivr.net/npm/libsodium-wrappers-sumo@0.8.3/+esm";
// import sodium from "https://cdn.jsdelivr.net/gh/jedisct1/libsodium.js/dist/browsers/sodium.js";

(async () => {
    await sodium.ready;
})()
export async function hashPassword(password, salt) {
    await sodium.ready;

    salt ??= sodium.randombytes_buf(sodium.crypto_pwhash_SALTBYTES);
    const key = sodium.crypto_pwhash(
        32, // dkLen
        password,
        salt,
        6, // t (opslimit)
        265 * 1024 * 1024, // bytes = 64 MiB
        sodium.crypto_pwhash_ALG_ARGON2ID13
    );
    return {
        salt,
        key
    }
}