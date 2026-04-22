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
