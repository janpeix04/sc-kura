/**
 * Converts an ArrayBuffer into a Base64 string
 *
 * - Used to serialize binary key data for storage or transport.
 *
 * @param {ArrayBuffer} buffer Binary data.
 * @returns {string} Base64 encoded string.
 */
function arrayBufferToBase64(buffer: ArrayBuffer) {
	return btoa(String.fromCharCode(...new Uint8Array(buffer)));
}

/**
 * Converts a Base64 string back into an ArrayBuffer.
 *
 * - Used to deserialize stored keys before importing.
 *
 * @param {string} base64 Base64 encoded string
 * @returns {ArrayBuffer} Binary data.
 */
function base64ToArrayBuffer(base64: string) {
	const binary = atob(base64);
	const bytes = new Uint8Array(binary.length);

	for (let i = 0; i < binary.length; i++) {
		bytes[i] = binary.charCodeAt(i);
	}

	return bytes.buffer;
}

function getRandomValues(size: number) {
	return crypto.getRandomValues(new Uint8Array(size));
}

/**
 * Generate a new RSA-OAEP key pair.
 *
 * - Uses 2048-bit modulus and SHA-256 hash.
 * - Public key is used for encryption.
 * - Private key is used for decryption.
 *
 * @returns {Promise<CryptoKeyPair>} The generated key pair.
 */
export async function generateRSAKeyPair() {
	return await crypto.subtle.generateKey(
		{
			name: 'RSA-OAEP',
			modulusLength: 2048,
			publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
			hash: 'SHA-256'
		},
		true,
		['encrypt', 'decrypt', 'wrapKey', 'unwrapKey']
	);
}

/**
 * Exports a public RSA key into SPKI format.
 *
 * - SPKI is the standard format for public keys.
 * - Result is an ArrayBuffer that can be encoded (e.g., base64) for storage or transmission.
 *
 * @param {CryptoKey} publicKey The RSA public key.
 * @returns {Promise<ArrayBuffer>} The exported key in SPKI format.
 */
export async function exportPublicKey(publicKey: CryptoKey) {
	return await crypto.subtle.exportKey('spki', publicKey);
}

/**
 * Exports a private RS key into PKCS#8 format.
 *
 * - PKCS#8 is the standard format for private keys.
 * - This should NEVER be stored unencrypted.
 *
 * @param {CryptoKey} privateKey The RSA private key.
 * @returns {Promise<ArrayBuffer>} The exported key in PKCS#8 format.
 */
export async function exportPrivateKey(privateKey: CryptoKey) {
	return await crypto.subtle.exportKey('pkcs8', privateKey);
}

/**
 * Encodes a key (ArrayBuffer) into Base64 format.
 *
 * @param {ArrayBuffer} buffer Key data.
 * @returns {string} Base64 encoded key.
 */
export function encodeKey(buffer: ArrayBuffer) {
	return arrayBufferToBase64(buffer);
}

/**
 * Generates a new RSA key pair and exports both keys as Base64 strings.
 *
 * - Public key is safe to store in backend.
 * - Private key MUST be encrypted before storing.
 *
 * @returns {Promise<{ publicKey: string; privateKey: string;}>}
 */
export async function createAndExportKeys() {
	const keyPair = await generateRSAKeyPair();

	const publicKeyBuffer = await exportPublicKey(keyPair.publicKey);
	const privateKeyBuffer = await exportPrivateKey(keyPair.privateKey);

	return {
		publicKey: encodeKey(publicKeyBuffer),
		privateKey: encodeKey(privateKeyBuffer)
	};
}

/**
 * Imports a Base64-encoded public key into a CryptoKey.
 *
 * - Expects SPKI format.
 * - Result can be used for encryption.
 *
 * @param {string} base64  Base64 encoded public key.
 * @returns {Promise<CryptoKey>} Imported public key.
 */
export async function importPublicKey(base64: string) {
	return await crypto.subtle.importKey(
		'spki',
		base64ToArrayBuffer(base64),
		{
			name: 'RSA-OAEP',
			hash: 'SHA-256'
		},
		true,
		['encrypt']
	);
}

/**
 * Imports base64-encoded private key into CryptoKey.
 *
 * - Expects PKCS#8 format.
 * - Result can be used for decryption.
 *
 * @param {string} base64 Base64 encoded private key.
 * @returns {Promise<CryptoKey>} Imported private key.
 */
export async function importPrivateKey(base64: string) {
	return await crypto.subtle.importKey(
		'pkcs8',
		base64ToArrayBuffer(base64),
		{
			name: 'RSA-OAEP',
			hash: 'SHA-256'
		},
		true,
		['decrypt']
	);
}

/**
 * Derives an AES-GCM encryption key from a user password using PBKDF2.
 *
 * - Uses PBKDF2 with SHA-256 for password stretching.
 * - Uses a cryptographic salt to prevent rainbow-table attacks.
 * - High iteration count (default: 600,000) increases brute-force costs.
 * - Produces a non-exportable AES-GCM 256-bit CryptoKey.
 *
 * Security notes:
 * - The same password + salt will always produce the same key.
 * - A different salt will produce a completely different key.
 * - This key should be used to encrypt sensitive data (e.g. private keys).
 *
 * @param {string} password User password used as key material.
 * @param {Uint8Array} salt Cryptographic salt (must be random and stored).
 * @param {number} iterations PBKDF2 iteration count (default: 600,000).
 * @returns {Promise<CryptoKey>} AES-GCM key derived from password.
 */
export async function deriveKeyFromPassword(
	password: string,
	salt: Uint8Array,
	iterations: number = 600000
) {
	const baseKey = await crypto.subtle.importKey(
		'raw',
		new TextEncoder().encode(password),
		{
			name: 'PBKDF2'
		},
		false,
		['deriveKey']
	);

	return await crypto.subtle.deriveKey(
		{
			name: 'PBKDF2',
			hash: 'SHA-256',
			iterations,
			salt: salt as BufferSource
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
 * Generates a random AES-GCM key for encrypting file data.
 *
 * @returns {Promise<CryptoKey>} AES-GCM 256-bit key.
 */
export async function generateAESKey() {
	return await crypto.subtle.generateKey(
		{
			name: 'AES-GCM',
			length: 256
		},
		true,
		['encrypt', 'decrypt']
	);
}

/**
 * Encrypts a file using AES-GCM.
 *
 * - AES-GCM provides confidenciality + integrity (tamper detection).
 * - A new random IV is generated per encryption (critical requirement).
 * - The IV must be stored alongside the ciphertext.
 *
 * Warning: Never reuse the same IV with the same key.
 *
 * @param {ArrayBuffer} file Raw file data to encrypt.
 * @param {CryptoKey} aesKey AES-GCM key used for encryption.
 * @returns {Promise<iv: Uint8Array; ciphertext: ArrayBuffer>}
 */
export async function encryptFile(file: ArrayBuffer, aesKey: CryptoKey) {
	const iv = getRandomValues(12);

	const ciphertext = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, aesKey, file);

	return {
		iv,
		ciphertext
	};
}

/**
 * Decrypts a file using AES-GCM.
 *
 * - AES-GCM provides confidentiality + integrity verification.
 * - Decryption will fail if the data was tampered with or corrupted.
 * - Requires the same AES key and IV used during encryption.
 *
 * Important:
 * - If the IV is incorrect or reused incorrectly, decryption will fail.
 * - AES-GCM automatically verifies integrity (authentication tag).
 *
 * @param {ArrayBuffer} ciphertext Encrypted file data.
 * @param {CryptoKey} key AES-GCM key used for decryption.
 * @param {Uint8Array} iv Initialization vector used during encryption.
 * @returns {Promise<ArrayBuffer>} Decrypted raw file data.
 */
export async function decryptFile(
	ciphertext: ArrayBuffer,
	key: CryptoKey,
	iv: Uint8Array<ArrayBuffer>
) {
	return await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext);
}

/**
 * Wraps an AES-GCM key using RSA-OAEP public key.
 *
 * - Produces an encrypted key blob safe for storage or transfer.
 *
 * @param {CryptoKey} aesKey AES-GCM key to wrap
 * @param {CryptoKey} publicKey RSA public key
 * @returns {Promise<ArrayBuffer>} Wrapped AES key
 */
export async function wrapAESKey(aesKey: CryptoKey, publicKey: CryptoKey) {
	return await crypto.subtle.wrapKey('raw', aesKey, publicKey, {
		name: 'RSA-OAEP'
	});
}

/**
 * Unwrap an AES-GCM key using RSA-OAEP private key.
 *
 * - Restores AES key from wrapped encrypted data.
 *
 * @param {ArrayBuffer} wrappedKey Encrypted AES key.
 * @param {CryptoKey} privateKey RSA private key.
 * @returns {Promise<CryptoKey>} AES-GCM key.
 */
export async function unwrapAESKey(wrappedKey: ArrayBuffer, privateKey: CryptoKey) {
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
 * Generates a cryptographically secure recovery key.
 *
 * - Produces 256 bits (32 bytes) of random entropy using the Web Crypto API.
 * - Encodes the binary key into Base64 for safe storage and user handling.
 * - This recovery key acts as a root backup secret for decrypting sensitive keys.
 *
 * Security properties:
 * - 256-bit entropy makes brute-force attacks computationally infeasible.
 * - Must be stored securely by the user (e.g., password manager or offline backup).
 * - If lost, encrypted data and private keys become permanently unrecoverable.
 *
 * @returns {Promise<string>} Base64-encoded recovery key.
 */
export async function generateRecoveryKey() {
	const bytes = getRandomValues(32);
	return arrayBufferToBase64(bytes.buffer);
}

/**
 * Imports a Base64-encoded recovery key into a CryptoKey usable by WebCrypto.
 *
 * - Decodes the Base64 representation back into raw binary form.
 * - Imports it as an AES-GCM key for symmetric encryption operations.
 * - The key is non-extractable by default security model of WebCrypto usage.
 *
 * Security properties:
 * - Key material remains client-side only.
 * - Enables secure encryption/decryption of private keys.
 *
 * @param {string} base64 - Base64 encoded recovery key.
 * @returns {Promise<CryptoKey>} AES-GCM CryptoKey used for recovery operations.
 */
export async function importRecoveryKey(base64: string) {
	const raw = base64ToArrayBuffer(base64);

	return await crypto.subtle.importKey('raw', raw, { name: 'AES-GCM' }, false, [
		'encrypt',
		'decrypt'
	]);
}

/**
 * Encrypts (protects) an RSA private key using a recovery key.
 *
 * - Exports the RSA private key into PKCS#8 format.
 * - Encrypts the exported key using AES-GCM with a recovery key.
 * - Generates a unique IV for each encryption operation.
 *
 * Security properties:
 * - Ensures confidentiality of the private key at rest.
 * - AES-GCM provides integrity protection (tamper detection).
 * - Without the recovery key, the private key cannot be restored.
 *
 * @param {CryptoKey} privateKey - RSA private key to protect.
 * @param {CryptoKey} recoveryKey - AES-GCM key derived from recovery secret.
 * @returns {Promise<{ iv: Uint8Array; encrypted: ArrayBuffer }>}
 *          Encrypted private key and IV required for decryption.
 */
export async function encryptPrivateKeyWithRecovery(privateKey: CryptoKey, recoveryKey: CryptoKey) {
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const exported = await crypto.subtle.exportKey('pkcs8', privateKey);

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, recoveryKey, exported);

	return {
		iv,
		encrypted
	};
}

/**
 * Recovers and reconstructs an RSA private key from encrypted storage.
 *
 * - Decrypts the encrypted PKCS#8 private key using AES-GCM.
 * - Validates integrity automatically via AES-GCM authentication tag.
 * - Re-imports the decrypted binary data into a usable CryptoKey.
 *
 * Security properties:
 * - Requires possession of the correct recovery key.
 * - Any tampering with ciphertext or IV will cause decryption failure.
 *
 * @param {ArrayBuffer} encrypted - Encrypted private key data.
 * @param {CryptoKey} recoveryKey - AES-GCM recovery key.
 * @param {Uint8Array} iv - Initialization vector used during encryption.
 * @returns {Promise<CryptoKey>} Restored RSA private key.
 */
export async function recoverPrivateKey(
	encrypted: ArrayBuffer,
	recoveryKey: CryptoKey,
	iv: Uint8Array<ArrayBuffer>
) {
	const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, recoveryKey, encrypted);

	return await crypto.subtle.importKey(
		'pkcs8',
		decrypted,
		{
			name: 'RSA-OAEP',
			hash: 'SHA-256'
		},
		true,
		['decrypt']
	);
}
