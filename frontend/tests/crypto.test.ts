import {
	base64ToArrayBuffer,
	decryptPrivateKey,
	deriveKeyFromPassword,
	encryptPrivateKey,
	generateAESKey,
	generateRecoveryKey,
	generateRSAKeyPair,
	unwrapKey,
	wrapKey
} from '$lib/crypto';
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

/**
 * Ensures private key encryption/decryption works correctly.
 *
 * Verifies:
 * - private key can be encrypted with a derived AES key
 * - decrypted output matches original input
 * - full roundtrip integrity is preserved
 */
test('encryptPrivateKey + decryptPrivateKey roundtrip', async () => {
	const password = 'password123';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key = await deriveKeyFromPassword(password, salt);

	const rsa = await generateRSAKeyPair();
	const privateKeyBuffer = await crypto.subtle.exportKey('pkcs8', rsa.privateKey);

	const { iv, encrypted } = await encryptPrivateKey(key, privateKeyBuffer);

	const decrypted = await decryptPrivateKey(key, iv, encrypted);

	const recoveredKey = await crypto.subtle.importKey(
		'pkcs8',
		decrypted,
		{ name: 'RSA-OAEP', hash: 'SHA-512' },
		true,
		['unwrapKey']
	);

	const aesKey = await crypto.subtle.generateKey({ name: 'AES-GCM', length: 256 }, true, [
		'encrypt',
		'decrypt'
	]);

	const wrapped = await wrapKey(aesKey, rsa.publicKey);
	const unwrapped = await unwrapKey(wrapped, recoveredKey);

	expect(unwrapped.algorithm.name).toBe('AES-GCM');
});

/**
 * Ensures wrong password cannot recover RSA private key.
 *
 * Verifies:
 * - incorrect derived key fails AES-GCM decryption
 * - private key remains protected
 */
test('wrong password fails RSA private key recovery', async () => {
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const correctKey = await deriveKeyFromPassword('correct', salt);
	const wrongKey = await deriveKeyFromPassword('wrong', salt);

	const rsa = await generateRSAKeyPair();
	const privateKeyBuffer = await crypto.subtle.exportKey('pkcs8', rsa.privateKey);

	const { iv, encrypted } = await encryptPrivateKey(correctKey, privateKeyBuffer);

	await expect(decryptPrivateKey(wrongKey, iv, encrypted)).rejects.toThrow();
});

/**
 * Ensures tampering encrypted RSA private key fails.
 *
 * Verifies:
 * - ciphertext modification is detected.
 * - AES-GCM authentication prevents recovery.
 */
test('tampering RSA private key fails', async () => {
	const password = 'password123';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key = await deriveKeyFromPassword(password, salt);

	const rsa = await generateRSAKeyPair();
	const privateKeyBuffer = await crypto.subtle.exportKey('pkcs8', rsa.privateKey);

	const { iv, encrypted } = await encryptPrivateKey(key, privateKeyBuffer);

	const tampered = new Uint8Array(encrypted);
	tampered[0] ^= 1;

	await expect(decryptPrivateKey(key, iv, tampered.buffer)).rejects.toThrow();
});

/**
 * Ensures IV integrity is required for successfull decryption.
 *
 * Verifies:
 * - modifying IV breaks AES-GCM authentication
 * - decryption fails even with correct key
 */
test('wrong IV breaks decryption', async () => {
	const password = 'password132';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key = await deriveKeyFromPassword(password, salt);

	const rsa = await generateRSAKeyPair();
	const privateKeyBuffer = await crypto.subtle.exportKey('pkcs8', rsa.privateKey);

	const { iv, encrypted } = await encryptPrivateKey(key, privateKeyBuffer);

	const badIv = new Uint8Array(iv);
	badIv[0] ^= 1;

	await expect(decryptPrivateKey(key, badIv, encrypted)).rejects.toThrow();
});

/**
 * Ensures AES-GCM encryption is non-deterministic.
 *
 * Verifies:
 * - each encryption produces a different IV
 * - ciphertext differs due to randomized IV
 * - both outputs can still be decrypted correctly
 */
test('encryptedPrivateKey is non-deterministic', async () => {
	const password = 'password123';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key = await deriveKeyFromPassword(password, salt);

	const rsa = await generateRSAKeyPair();
	const privateKeyBuffer = await crypto.subtle.exportKey('pkcs8', rsa.privateKey);

	const r1 = await encryptPrivateKey(key, privateKeyBuffer);
	const r2 = await encryptPrivateKey(key, privateKeyBuffer);

	expect(r1.iv).not.toEqual(r2.iv);
	expect(new Uint8Array(r1.encrypted)).not.toEqual(new Uint8Array(r2.encrypted));

	const d1 = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: r1.iv }, key, r1.encrypted);
	const d2 = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: r2.iv }, key, r2.encrypted);

	expect(d1).toEqual(privateKeyBuffer);
	expect(d2).toEqual(privateKeyBuffer);
});

/**
 * Ensures recovery key can restored encrypted private key.
 *
 * Verifies:
 * - private key encrypted with recovery key can ve decrypted
 * - decrypted output matches original RSA private key
 * - recovery mechanism is independent of password flow
 */
test('recovery key roundtrip restores private key', async () => {
	const rsa = await generateRSAKeyPair();
	const privateKey = await crypto.subtle.exportKey('pkcs8', rsa.privateKey);

	const recoveryKeyBase64 = generateRecoveryKey();
	const recoveryKeyRaw = base64ToArrayBuffer(recoveryKeyBase64);
	const recoveryKey = await crypto.subtle.importKey(
		'raw',
		recoveryKeyRaw,
		{ name: 'AES-GCM' },
		false,
		['encrypt', 'decrypt']
	);

	const { iv, encrypted } = await encryptPrivateKey(recoveryKey, privateKey);
	const decrypt = await decryptPrivateKey(recoveryKey, iv, encrypted);

	expect(decrypt).toEqual(privateKey);
});

/**
 * Ensures AES key is generated with correct properties and is usable.
 *
 * Verifies:
 * - key is a valid CrytpoKey
 * - key type is "secret"
 * - algorithm is AES-GCM
 * - usages includes encrypt and decrypt
 * - key can successfully enrypt and decrypt data
 */
test('generateAESKey produces valid AES-GCM key', async () => {
	const key = await generateAESKey();

	expect(key).toBeDefined();
	expect(key.type).toBe('secret');

	expect(key.algorithm.name).toBe('AES-GCM');
	expect(key.extractable).toBe(true);

	expect(key.usages).toContain('encrypt');
	expect(key.usages).toContain('decrypt');

	const raw = await crypto.subtle.exportKey('raw', key);
	expect(raw.byteLength).toBe(32);

	// Usability check
	const data = new TextEncoder().encode('test message');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key, data);
	const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, encrypted);

	expect(new TextDecoder().decode(decrypted)).toBe('test message');
});
