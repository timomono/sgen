import { sha256 } from './hash.js';

function randomBytes(n) {
    return crypto.getRandomValues(new Uint8Array(n));
}

function b64ToBytes(s) {
    return Uint8Array.from(atob(s), c => c.charCodeAt(0));
}

export async function createWebAuthn(username) {
    const challenge = randomBytes(32);
    // const userId = b64ToBytes(await sha256(username));
    const userId = randomBytes(16);

    const options = {
        challenge,
        rp: {
            name: 'S-Gen',
            id: location.hostname || 'localhost',
        },
        user: {
            id: userId,
            name: username,
            displayName: username,
        },
        pubKeyCredParams: [
            { type: 'public-key', alg: -7 },   // ES256
            { type: 'public-key', alg: -257 },  // RS256 fallback
        ],
        authenticatorSelection: {
            residentKey: 'required',
            userVerification: 'required',
            // userVerification: 'preferred',
        },
        extensions: {
            // Signal that we want PRF support
            prf: {}
        },
        timeout: 60000,
    }
    const credential = await navigator.credentials.create({ publicKey: options });
    const ext = credential.getClientExtensionResults();
    const isSupported = ext.prf?.enabled;

    if (!isSupported) {
        throw new Error("PRF is not supported in this browser.");
    }
}

export async function getWebAuthn() {
    const challenge = randomBytes(32);
    // const saltBytes = new Uint8Array(32);
    // const saltBytes = randomBytes(32);
    const saltBytes = b64ToBytes(await sha256("encryption-key-v1"));
    const options = {
        challenge,
        // allowCredentials: [{
        //     type: 'public-key',
        //     id: b64ToBytes(await sha256(username)),
        // }],
        userVerification: 'required',
        extensions: {
            prf: {
                eval: {
                    first: saltBytes.buffer,
                }
            }
        },
        timeout: 60000,
    };

    const credential = await navigator.credentials.get({ publicKey: options });

    const ext = credential.getClientExtensionResults();
    const prf = ext.prf?.results;

    if (!prf?.first) {
        throw new Error("PRF not supported or not returned");
    }

    const keyMaterial = new Uint8Array(prf.first);
    console.log('Derived key material:', keyMaterial);

    return keyMaterial;
}