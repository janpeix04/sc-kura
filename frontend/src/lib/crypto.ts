import type { EncryptedFolderPublic } from './client';
import type { DecryptedFolder } from './schemas/types';

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
 * Converts an ArrayBuffer into a Base64-encoded string.
 *
 * - Iterates through the raw bytes of the buffer.
 * - Converts each byte into a binary string representation.
 * - Uses `btoa()` to encode the binary string into Base64.
 *
 * Security notes:
 * - Base64 is NOT encryption — it is only an encoding format.
 * - It does not provide confidentiality or integrity.
 * - Commonly used for safely transporting binary data (e.g. keys, IVs, ciphertext)
 *   in text-based formats like JSON or HTTP payloads.
 *
 * @param {ArrayBuffer | Uint8Array} buffer The binary data to encode.
 * @returns {string} Base64-encoded string representation of the input buffer.
 */
export function arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array) {
	const bytes = buffer instanceof Uint8Array ? buffer : new Uint8Array(buffer);

	let binary = '';
	for (let i = 0; i < bytes.length; i++) {
		binary += String.fromCharCode(bytes[i]);
	}

	return btoa(binary);
}

/**
 * Converts a Base64-encoded string back into an ArrayBuffer.
 *
 * - Decodes Base64 into a binary string using `atob()`.
 * - Converts each character into its byte value.
 * - Reconstructs the original binary buffer.
 *
 * Security notes:
 * - Base64 is only encoding, not encryption.
 * - Input must be trusted or validated if coming from external sources.
 *
 * @param {string} base64 Base64-encoded string.
 * @returns {ArrayBuffer} Decoded binary data.
 */
export function base64ToArrayBuffer(base64: string) {
	const binary = atob(base64);
	const bytes = new Uint8Array(binary.length);

	for (let i = 0; i < binary.length; i++) {
		bytes[i] = binary.charCodeAt(i);
	}

	return bytes.buffer;
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

/**
 * Generates a random recovery key for account/key recovery purposes.
 *
 * - Creates 32 cryptographically secure random bytes (256-bit strength).
 * - Encodes the raw binary data into Base64 for safe storage/transmission.
 *
 * Security notes:
 * - The recovery key is generated using `crypto.getRandomValues`, which is
 *   cryptographically secure and suitable for sensitive operations.
 * - This value should be treated like a password: anyone with it can potentially
 *   restore access to encrypted data.
 * - Must be stored securely (e.g. password manager, secure backup storage).
 * - Base64 encoding is NOT encryption; it only makes binary data text-safe.
 *
 * @returns {Promise<string>} Base64-encoded 256-bit recovery key.
 */
export function generateRecoveryKey() {
	const baseKey = getRandomValues(32);
	return arrayBufferToBase64(baseKey.buffer);
}

/**
 * Imports a cryptographic key into the Web Crypto API as a CryptoKey.
 *
 * - Converts raw or serialized key material into a usable CryptoKey object.
 * - Supports multiple key formats and algorithms (RSA, AES, HMAC, EC, etc.).
 * - Required when restoring keys from storage (e.g., database, Base64, ArrayBuffer).
 *
 * Supported formats:
 * - 'raw'   → symmetric keys (e.g., AES, HMAC)
 * - 'pkcs8' → private keys (e.g., RSA private key)
 * - 'spki'  → public keys (e.g., RSA public key)
 *
 * Security notes:
 * - If `extractable` is false, the key cannot be exported again (more secure).
 * - `keyUsages` must match the intended operations (e.g., encrypt, decrypt).
 * - Imported keys must match the algorithm they were originally created with.
 *
 * @param {'raw' | 'pkcs8' | 'spki'} format Format of the key data.
 * @param {BufferSource} keyData Raw or encoded key data (ArrayBuffer, Uint8Array, etc.).
 * @param {AlgorithmIdentifier | RsaHashedImportParams | EcKeyImportParams | HmacImportParams | AesKeyAlgorithm} algorithm
 * The algorithm definition (e.g., RSA-OAEP, AES-GCM).
 * @param {boolean} extractable Whether the key can be exported after import.
 * @param {ReadonlyArray<KeyUsage>} keyUsages Allowed operations for the key (e.g., ['encrypt', 'decrypt']).
 *
 * @returns {Promise<CryptoKey>} The imported CryptoKey ready for cryptographic operations.
 */
export async function importKey(
	format: 'raw' | 'pkcs8' | 'spki',
	keyData: BufferSource,
	algorithm:
		| AlgorithmIdentifier
		| RsaHashedImportParams
		| EcKeyImportParams
		| HmacImportParams
		| AesKeyAlgorithm,
	extractable: boolean,
	keyUsages: ReadonlyArray<KeyUsage>
) {
	return await crypto.subtle.importKey(format, keyData, algorithm, extractable, keyUsages);
}

/**
 * Exports a CryptoKey into a raw or standardized binary format.
 *
 * - Converts a CryptoKey into an ArrayBuffer so it can be stored,
 *   transmitted, or further processed (e.g., encrypted or Base64 encoded).
 * - Required when persisting keys in a database or sending them over a network.
 *
 * Supported formats:
 * - 'raw'   → symmetric keys (e.g., AES, HMAC)
 * - 'pkcs8' → private keys (e.g., RSA private key)
 * - 'spki'  → public keys (e.g., RSA public key)
 *
 * Security notes:
 * - The key MUST have been created/imported with `extractable: true`,
 *   otherwise export will fail.
 * - Exported key material is sensitive and should be protected
 *   (e.g., encrypted before storage).
 *
 * @param {'raw' | 'pkcs8' | 'spki'} format Format to export the key into.
 * @param {CryptoKey} key The CryptoKey to export.
 *
 * @returns {Promise<ArrayBuffer>} The exported key as binary data.
 */
export async function exportKey(format: 'raw' | 'pkcs8' | 'spki', key: CryptoKey) {
	return await crypto.subtle.exportKey(format, key);
}

/**
 * Generates a new symmetric AES key for encryption and decryption.
 *
 * - Uses AES-GCM with a 256-bit key length
 * - The key is extractable, meaning it can be exported
 * - Intended for use with the Web Crypto API
 *
 * @returns {Promise<CryptoKey>}
 */
export async function generateAESKey() {
	return await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
		'encrypt',
		'decrypt'
	]);
}

/**
 * Encrypts file data using AES-GCM with a randomly generated IV.
 *
 * - Uses AES-GCM (256-bit key) to provide both confidentiality and integrity.
 * - A unique 96-bit IV is generated for each encryption operation.
 * - Returns the IV alongside the ciphertext, as it is required for decryption.
 *
 * ⚠️ Notes:
 * - The entire file is processed as an ArrayBuffer, making this suitable
 *   only for small to moderate file sizes.
 * - For large files, a chunked or streaming approach would be more appropriate
 *   to avoid high memory usage.
 * - Reusing the same IV with the same key must be avoided, as it breaks
 *   AES-GCM security guarantees.
 *
 * @param {CryptoKey} key - AES-GCM key used for encryption.
 * @param {ArrayBuffer} data - File data to encrypt.
 * @returns {Promise<{ iv: Uint8Array, encrypted: ArrayBuffer }>}
 * An object containing the initialization vector and encrypted data.
 */
export async function encryptFile(key: CryptoKey, data: ArrayBuffer) {
	const iv = getRandomValues(12);

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, data);

	return {
		iv,
		encrypted
	};
}

/**
 * Decrypts file data encrypted with AES-GCM.
 *
 * - Uses the same AES-GCM key and IV that were used during encryption.
 * - AES-GCM provides authenticated decryption, ensuring both
 *   confidentiality and integrity of the data.
 * - If the key, IV, or ciphertext has been altered, decryption will fail.
 *
 * ⚠️ Notes:
 * - The IV must match exactly the one used during encryption.
 * - Decryption will throw an error if authentication fails (e.g., wrong key,
 *   modified ciphertext, or incorrect IV).
 * - The entire encrypted data is processed in memory, making this suitable
 *   only for small to moderate file sizes.
 *
 * @param {CryptoKey} key - AES-GCM key used for decryption.
 * @param {BufferSource} iv - Initialization vector used during encryption.
 * @param {ArrayBuffer} encryptedData - Encrypted file data.
 * @returns {Promise<ArrayBuffer>} A promise that resolves to the decrypted file data.
 */
export async function decryptFile(key: CryptoKey, iv: BufferSource, encryptedData: ArrayBuffer) {
	return await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, encryptedData);
}

export async function decryptFolder(folder: EncryptedFolderPublic, privateKey: CryptoKey) {
	const wrappedKey = base64ToArrayBuffer(folder.encrypted_key);
	const key = await unwrapKey(wrappedKey, privateKey);

	const encryptedNameBuffer = base64ToArrayBuffer(folder.encrypted_name);
	const iv = base64ToArrayBuffer(folder.iv);

	const encodedName = await decryptFile(key, iv, encryptedNameBuffer);
	const name = new TextDecoder().decode(encodedName);

	return {
		id: folder.id,
		key,
		name,
		type: folder.type ?? 'directory',
		size: folder.size,
		createdAt: folder.created_at,
		parentId: folder.parent_id
	} as DecryptedFolder;
}
