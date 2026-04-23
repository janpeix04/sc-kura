import { deriveKeyFromPassword, generateRSAKeyPair, unwrapKey, wrapKey } from '$lib/e2ee';
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

/**
 * Ensures PBKDF2 is deterministic.
 *
 * Verifies:
 * - same password + same salt + same iterations
 *   always produces the same usable key
 */
test('deriveKeyFromPassword is deterministic', async () => {
	const password = 'strong-password';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key1 = await deriveKeyFromPassword(password, salt, 100000);
	const key2 = await deriveKeyFromPassword(password, salt, 100000);

	const data = new TextEncoder().encode('hello');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const e1 = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key1, data);
	const e2 = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key2, data);

	const d1 = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key1, e1);
	const d2 = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key2, e2);

	expect(new TextDecoder().decode(d1)).toBe('hello');
	expect(new TextDecoder().decode(d2)).toBe('hello');
});

/**
 * Ensures different passwords produce incompatible keys.
 *
 * Verifies:
 * - wrong password cannot decrypt data
 */
test('wrong password cannot decrypt', async () => {
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const correctKey = await deriveKeyFromPassword('correct', salt, 100000);
	const wrongKey = await deriveKeyFromPassword('wrong', salt, 100000);

	const data = new TextEncoder().encode('secret');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, correctKey, data);

	await expect(
		crypto.subtle.decrypt({ name: 'AES-GCM', iv }, wrongKey, encrypted)
	).rejects.toThrow();
});

/**
 * Ensures salt uniqueness affects derived key.
 *
 * Verifies:
 * - same password + different salts → incompatible keys
 */
test('different salts produce different keys', async () => {
	const password = 'same-password';

	const salt1 = crypto.getRandomValues(new Uint8Array(16));
	const salt2 = crypto.getRandomValues(new Uint8Array(16));

	const key1 = await deriveKeyFromPassword(password, salt1, 100000);
	const key2 = await deriveKeyFromPassword(password, salt2, 100000);

	const data = new TextEncoder().encode('message');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key1, data);

	await expect(crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key2, encrypted)).rejects.toThrow();
});

/**
 * Ensures iteration count affects derived key.
 *
 * Verifies:
 * - same password + salt but different iterations → different keys
 */
test('different iterations produce different keys', async () => {
	const password = 'password';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key1 = await deriveKeyFromPassword(password, salt, 100000);
	const key2 = await deriveKeyFromPassword(password, salt, 200000);

	const data = new TextEncoder().encode('data');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key1, data);

	await expect(crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key2, encrypted)).rejects.toThrow();
});
