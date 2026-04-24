/**
 * Generates a cryptographically secure array of random bytes.
 *
 * - Uses the Web Crypto API (`crypto.getRandomValues`) which provides
 *   strong, non-deterministic randomness suitable for cryptographic use.
 * - Commonly used for generating salts, IVs (initialization vectors),
 *   nonces, tokens, and other secure random data.
 *
 * Security notes:
 * - This is NOT the same as `Math.random()` and must be used for any
 *   security-sensitive randomness.
 * - The output is suitable for direct use in cryptographic operations.
 *
 * @param {number} size Number of random bytes to generate.
 * @returns {Uint8Array} A typed array filled with secure random values.
 */
export function getRandomValues(size: number) {
	return crypto.getRandomValues(new Uint8Array(size));
}

/**
 * Generates an RSA-OAEP key pair used for key wrapping and unwrapping.
 *
 * - Uses a 4096-bit modulus for strong asymmetric security.
 * - Uses SHA-512 as the hashing algorithm for OAEP padding.
 * - Public key is used to wrap (encrypt) symmetric keys.
 * - Private key is used to unwrap (decrypt) and recover symmetric keys.
 *
 * Security notes:
 * - This key pair is NOT intended for bulk encryption (use AES for data).
 * - Designed specifically for securely transporting or storing AES keys.
 * - Larger key size (4096 bits) increases security but reduces performance.
 *
 * @returns {Promise<CryptoKeyPair>} Generated RSA key pair.
 */
export async function generateRSAKeyPair() {
	return await crypto.subtle.generateKey(
		{
			name: 'RSA-OAEP',
			modulusLength: 4096,
			publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
			hash: 'SHA-512'
		},
		true,
		['wrapKey', 'unwrapKey']
	);
}

/**
 * Wraps a symmetric CryptoKey using an RSA-OAEP public key.
 *
 * - Encrypts (wraps) a raw AES key so it can be safely stored or transmitted.
 * - Uses RSA-OAEP as the asymmetric encryption algorithm.
 *
 * Typical use case:
 * - Protecting AES keys before saving them to a database or sending them over the network.
 *
 * @param {CryptoKey} key The symmetric key to wrap (e.g. AES-GCM key).
 * @param {CryptoKey} publicKey RSA public key used for wrapping.
 * @returns {Promise<ArrayBuffer>} The wrapped (encrypted) key.
 */
export async function wrapKey(key: CryptoKey, publicKey: CryptoKey) {
	return await crypto.subtle.wrapKey('raw', key, publicKey, { name: 'RSA-OAEP' });
}

/**
 * Unwraps a previously wrapped symmetric key using an RSA-OAEP private key.
 *
 * - Decrypts the wrapped key back into a usable CryptoKey.
 * - Restores an AES-GCM key for encryption/decryption operations.
 *
 * Security notes:
 * - Requires the correct RSA private key to succeed.
 * - Any tampering with the wrapped data will cause decryption failure.
 *
 * Typical use case:
 * - Recovering AES keys for decrypting stored or received encrypted data.
 *
 * @param {ArrayBuffer} wrappedKey The encrypted (wrapped) AES key.
 * @param {CryptoKey} privateKey RSA private key used for unwrapping.
 * @returns {Promise<CryptoKey>} The restored AES-GCM key.
 */
export async function unwrapKey(wrappedKey: ArrayBuffer, privateKey: CryptoKey) {
	return await crypto.subtle.unwrapKey(
		'raw',
		wrappedKey,
		privateKey,
		{ name: 'RSA-OAEP' },
		{ name: 'AES-GCM', length: 256 },
		true,
		['encrypt', 'decrypt']
	);
}

/**
 * Derives a symmetric AES-GCM key from a user-provided password using PBKDF2.
 *
 * - Uses PBKDF2 with SHA-512 for strong password-based key derivation.
 * - Applies a configurable number of iterations to increase resistance
 *   against brute-force and dictionary attacks.
 * - Requires a cryptographic salt to ensure unique derived keys per user.
 * - Produces a 256-bit AES-GCM key for secure encryption/decryption.
 *
 * Security notes:
 * - The same password + salt + iterations will always produce the same key (deterministic).
 * - Changing the salt results in a completely different key.
 * - Higher iteration counts increase security but also computation time.
 * - The derived key is non-extractable (cannot be exported), improving security.
 *
 * Typical use cases:
 * - Encrypting sensitive data with a user password.
 * - Protecting private keys or recovery material.
 *
 * @param {string} password User password used as input key material.
 * @param {BufferSource} salt Cryptographic salt (must be random and stored).
 * @param {number} iterations Number of PBKDF2 iterations (default: 100,000).
 * @returns {Promise<CryptoKey>} Derived AES-GCM CryptoKey.
 */
export async function deriveKeyFromPassword(
	password: string,
	salt: BufferSource,
	iterations: number = 100000
) {
	const baseKey = await crypto.subtle.importKey(
		'raw',
		new TextEncoder().encode(password),
		{ name: 'PBKDF2' },
		false,
		['deriveKey']
	);

	return await crypto.subtle.deriveKey(
		{
			name: 'PBKDF2',
			hash: 'SHA-512',
			iterations,
			salt
		},
		baseKey,
		{
			name: 'AES-GCM',
			length: 256
		},
		false,
		['encrypt', 'decrypt']
	);
}

/**
 * Encrypts a private key using a password-derived AES-GCM key.
 *
 * - Uses AES-GCM to provide both confidentiality and integrity (authentication).
 * - Generates a new random IV (12 bytes) for each encryption operation.
 * - Returns both the encrypted data and IV (required for decryption).
 *
 * Security notes:
 * - Never reuse the same IV with the same key.
 * - The derived key should come from a secure KDF (e.g., PBKDF2).
 * - AES-GCM ensures that any tampering with the ciphertext will cause decryption to fail.
 *
 * @param {CryptoKey} derivedKey AES-GCM key derived from a password.
 * @param {BufferSource} privateKey Raw private key data (e.g., PKCS#8 ArrayBuffer).
 * @returns {Promise<{ encrypted: ArrayBuffer; iv: Uint8Array }>}
 * An object containing:
 * - `encrypted`: the encrypted private key (ciphertext)
 * - `iv`: initialization vector required for decryption
 */
export async function encryptPrivateKey(derivedKey: CryptoKey, privateKey: BufferSource) {
	const iv = getRandomValues(12);

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, derivedKey, privateKey);

	return {
		encrypted,
		iv
	};
}

/**
 * Decrypts a private key encrypted with AES-GCM using a password-derived key.
 *
 * - Uses AES-GCM to restore the original private key.
 * - Requires the same derived key and IV used during encryption.
 * - Automatically verifies integrity via authentication tag.
 *
 * Security notes:
 * - Decryption will fail if:
 *   - the key is incorrect (wrong password),
 *   - the IV is incorrect,
 *   - or the ciphertext has been tampered with.
 *
 * @param {CryptoKey} derivedKey AES-GCM key derived from a password.
 * @param {BufferSource} iv Initialization vector used during encryption.
 * @param {ArrayBuffer} encryptedPrivateKey Encrypted private key data.
 * @returns {Promise<ArrayBuffer>} Decrypted private key (original binary data).
 */
export async function decryptPrivateKey(
	derivedKey: CryptoKey,
	iv: BufferSource,
	encryptedPrivateKey: ArrayBuffer
) {
	return await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, derivedKey, encryptedPrivateKey);
}
