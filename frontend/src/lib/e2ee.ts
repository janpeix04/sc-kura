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
		['encrypt', 'decrypt', 'wrapKey', 'unwrapKey']
	);
}
