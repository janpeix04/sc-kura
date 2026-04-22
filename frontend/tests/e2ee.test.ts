import { generateRSAKeyPair, unwrapKey, wrapKey } from '$lib/e2ee';
import { expect, test } from 'vitest';

/**
 * Ensures RSA key pair is generated correctly.
 *
 * Verifies:
 * - both public and private keys exist
 * - keys are usable CryptoKey objects
 * - algorithm matches RSA-OAEP
 */
test('RSA key pair generation', async () => {
	const keyPair = await generateRSAKeyPair();

	expect(keyPair.publicKey).toBeDefined();
	expect(keyPair.privateKey).toBeDefined();

	expect(keyPair.publicKey.type).toBe('public');
	expect(keyPair.privateKey.type).toBe('private');

	expect(keyPair.publicKey.algorithm.name).toBe('RSA-OAEP');
	expect(keyPair.privateKey.algorithm.name).toBe('RSA-OAEP');
});

/**
 * Ensures AES key can be wrapped and unwrapped correctly using RSA-OAEP.
 *
 * Verifies:
 * - key is successfully wrapped using RSA public key
 * - wrapped key can be unwrapped with RSA private key
 * - resulting key works for AES-GCM encryption/decryption
 */
test('wrapKey + unwrapKey roundtrip', async () => {
	const rsa = await generateRSAKeyPair();

	const aesKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
		'encrypt',
		'decrypt'
	]);

	const wrapped = await wrapKey(aesKey, rsa.publicKey);
	const unwrapped = await unwrapKey(wrapped, rsa.privateKey);

	const data = new TextEncoder().encode('hello world');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, unwrapped, data);

	const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, unwrapped, encrypted);

	expect(new TextDecoder().decode(decrypted)).toBe('hello world');
});

/**
 * Ensures RSA key isolation between different keypairs.
 *
 * Verifies:
 * - AES key wrapped with one RSA pair cannot be unwrapped by another
 * - unwrap fails securely with wrong private key
 */
test('wrong RSA key cannot unwrap AES key', async () => {
	const rsa1 = await generateRSAKeyPair();
	const rsa2 = await generateRSAKeyPair();

	const aesKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
		'encrypt',
		'decrypt'
	]);

	const wrapped = await wrapKey(aesKey, rsa1.publicKey);

	await expect(unwrapKey(wrapped, rsa2.privateKey)).rejects.toThrow();
});

/**
 * Ensures unwrapKey returns a valid AES-GCM CryptoKey.
 *
 * Verifies:
 * - key type is correct ("secret")
 * - algorithm is AES-GCM
 * - key can be used for encryption operations
 */
test('unwrapKey returns valid AES key', async () => {
	const rsa = await generateRSAKeyPair();
	const aesKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
		'encrypt',
		'decrypt'
	]);

	const wrapped = await wrapKey(aesKey, rsa.publicKey);
	const unwrapped = await unwrapKey(wrapped, rsa.privateKey);

	expect(unwrapped.type).toBe('secret');
	expect(unwrapped.algorithm.name).toBe('AES-GCM');
});
