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
		['encrypt', 'decrypt']
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
