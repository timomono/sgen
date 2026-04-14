// TODO: The code by ChatGPT, review required
import { argon2id, argon2i, argon2d } from 'https://cdn.jsdelivr.net/npm/@noble/hashes@2.2.0/argon2.js'
import { bytesToHex, hexToBytes } from 'https://cdn.jsdelivr.net/npm/@noble/hashes@2.2.0/utils.js'

// ─── Encoding helpers ─────────────────────────────────────────────────────────

const encoder = new TextEncoder();
const decoder = new TextDecoder();

/** @param {string} str @returns {Uint8Array} */
const toBytes = (str) => encoder.encode(str);

/** @param {Uint8Array} bytes @returns {string} */
const fromBytes = (bytes) => decoder.decode(bytes);

// ─── Variant map ──────────────────────────────────────────────────────────────

export const Algorithm = Object.freeze({
    argon2id,
    argon2i,
    argon2d,
});

// ─── Default options ──────────────────────────────────────────────────────────

/** @typedef {{ t?: number, m?: number, p?: number, dkLen?: number, type?: Function }} Argon2Options */

/** @type {Required<Argon2Options>} */
export const defaults = Object.freeze({
    type: argon2id, // recommended hybrid variant
    t: 6,        // time cost (iterations)
    m: 65536,    // memory cost in KiB (64 MiB)
    p: 2,        // parallelism
    dkLen: 32,       // derived key length in bytes
});

// ─── Salt utilities ───────────────────────────────────────────────────────────

const SALT_BYTES = 16;

/**
 * Generate a cryptographically random salt using the Web Crypto API.
 * @param {number} [length=16]
 * @returns {Uint8Array}
 */
export function generateSalt(length = SALT_BYTES) {
    return crypto.getRandomValues(new Uint8Array(length));
}

// ─── Encoded hash format ──────────────────────────────────────────────────────
//
// We store hashes as a custom PHC-like string so the salt is included:
//   $argon2id$v=1$t=3,m=65536,p=1$<salt-hex>$<hash-hex>
//
// This is self-contained — no need to store the salt separately.

const VARIANT_NAME = new Map([
    [argon2id, "argon2id"],
    [argon2i, "argon2i"],
    [argon2d, "argon2d"],
]);

/**
 * Encode a raw hash + metadata into a storable string.
 * @internal
 */
function encode(hashBytes, saltBytes, opts) {
    const variant = VARIANT_NAME.get(opts.type) ?? "argon2id";
    return [
        "",
        variant,
        "v=19",
        `t=${opts.t},m=${opts.m},p=${opts.p}`,
        bytesToHex(saltBytes),
        bytesToHex(hashBytes),
    ].join("$");
}

/**
 * Parse a stored encoded hash string back into its components.
 * @internal
 * @param {string} encoded
 */
function decode(encoded) {
    const parts = encoded.split("$");
    // parts: ["", variant, "v=1", "t=N,m=N,p=N", saltHex, hashHex]
    if (parts.length !== 6 || parts[0] !== "") {
        throw new Error("Invalid encoded hash format");
    }

    const [, variantName, , paramStr, saltHex, hashHex] = parts;

    const variantFn = [...VARIANT_NAME.entries()].find(([, n]) => n === variantName)?.[0];
    if (!variantFn) throw new Error(`Unknown variant: ${variantName}`);

    const paramPairs = Object.fromEntries(
        paramStr.split(",").map((kv) => {
            const [k, v] = kv.split("=");
            return [k, Number(v)];
        })
    );

    const hashBytes = hexToBytes(hashHex);

    return {
        type: variantFn,
        t: paramPairs.t,
        m: paramPairs.m,
        p: paramPairs.p,
        saltBytes: hexToBytes(saltHex),
        hashBytes,
        dkLen: hashBytes.length,
    };
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Hash a plain-text password.
 *
 * Returns a self-contained encoded string (includes variant, params, salt, hash).
 * Safe to store directly in a database.
 *
 * @param {string}         password
 * @param {Argon2Options}  [opts]       Override defaults.
 * @param {Uint8Array}     [salt]       Custom salt (auto-generated if omitted).
 * @returns {Promise<string>}           Encoded hash string.
 *
 * @example
 * const hash = await hashPassword("my-secret");
 */
export async function hashPassword(password, opts = {}, salt) {
    if (typeof password !== "string" || password.length === 0) {
        throw new TypeError("password must be a non-empty string");
    }

    const o = { ...defaults, ...opts };
    const saltBytes = salt ?? generateSalt();
    const passwordBytes = toBytes(password);

    const hashBytes = o.type(passwordBytes, saltBytes, {
        t: o.t,
        m: o.m,
        p: o.p,
        dkLen: o.dkLen,
    });

    return encode(hashBytes, saltBytes, o);
}

/**
 * Verify a plain-text password against a stored encoded hash.
 *
 * @param {string} encoded    The stored encoded hash string.
 * @param {string} password   The plain-text password to verify.
 * @returns {Promise<boolean>}
 *
 * @example
 * const ok = await verifyPassword(storedHash, "my-secret");
 */
export async function verifyPassword(encoded, password) {
    if (!encoded || !password) {
        throw new TypeError("encoded and password must be non-empty strings");
    }

    const { type, t, m, p, dkLen, saltBytes, hashBytes } = decode(encoded);
    const passwordBytes = toBytes(password);

    const candidate = type(passwordBytes, saltBytes, { t, m, p, dkLen });

    // Constant-time comparison to mitigate timing attacks
    if (candidate.length !== hashBytes.length) return false;
    let diff = 0;
    for (let i = 0; i < candidate.length; i++) {
        diff |= candidate[i] ^ hashBytes[i];
    }
    return diff === 0;
}

/**
 * Returns true when the stored hash uses different parameters than the
 * supplied options (e.g. after tightening security settings).
 *
 * @param {string}         encoded
 * @param {Argon2Options}  [opts]   Defaults to the library defaults.
 * @returns {boolean}
 *
 * @example
 * if (needsRehash(user.passwordHash)) {
 *   user.passwordHash = await hashPassword(plainPassword);
 * }
 */
export function needsRehash(encoded, opts = {}) {
    const o = { ...defaults, ...opts };
    const variantName = VARIANT_NAME.get(o.type) ?? "argon2id";
    const parsed = decode(encoded);
    return (
        parsed.type !== o.type ||
        parsed.t !== o.t ||
        parsed.m !== o.m ||
        parsed.p !== o.p ||
        parsed.dkLen !== o.dkLen
    );
}