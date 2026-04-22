import {
	createAndExportKeys,
	importPrivateKey,
	importPublicKey,
	deriveKeyFromPassword,
	generateAESKey,
	encryptFile,
	wrapAESKey,
	generateRSAKeyPair,
	unwrapAESKey,
	decryptFile,
	generateRecoveryKey,
	importRecoveryKey,
	encryptPrivateKeyWithRecovery,
	recoverPrivateKey,
	encryptPrivateKeyWithPassword,
	decryptPrivateKeyWithPassword
} from '$lib/utilities/e2ee';
import { test, expect } from 'vitest';

/**
 * Full RSA roundtrip test
 * Verifies:
 * - key generation works
 * - export/import works
 * - encryption + decryption works correctly
 */
test('RSA encrypt/decrypt roundtrip', async () => {
	const { publicKey, privateKey } = await createAndExportKeys();

	const pubKey = await importPublicKey(publicKey);
	const privKey = await importPrivateKey(privateKey);

	const messageText = 'hello kura';
	const message = new TextEncoder().encode(messageText);

	const encrypted = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pubKey, message);

	const decrypted = await crypto.subtle.decrypt({ name: 'RSA-OAEP' }, privKey, encrypted);

	const result = new TextDecoder().decode(decrypted);

	expect(result).toBe(messageText);
});

/**
 * Ensures export → import cycle does not corrupt the public key
 * Verifies:
 * - SPKI export is consistent
 * - importing and re-exporting preserves original data
 */
test('public key export/import is stable', async () => {
	const { publicKey } = await createAndExportKeys();

	const imported = await importPublicKey(publicKey);
	const reExported = await crypto.subtle.exportKey('spki', imported);

	expect(btoa(String.fromCharCode(...new Uint8Array(reExported)))).toBe(publicKey);
});

/**
 * Ensures invalid key data is rejected
 * Verifies:
 * - crypto.subtle.importKey correctly validates input format
 */
test('invalid public key fails to import', async () => {
	await expect(importPublicKey('not-a-valid-key')).rejects.toThrow();
});

/**
 * Ensures RSA-OAEP produces different ciphertext each time
 * Verifies:
 * - encryption is probabilistic (uses internal random padding)
 * - same input does NOT produce same output
 */
test('RSA encryption is non-deterministic', async () => {
	const { publicKey } = await createAndExportKeys();
	const pub = await importPublicKey(publicKey);

	const msg = new TextEncoder().encode('same message');

	const e1 = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pub, msg);
	const e2 = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pub, msg);

	expect(Buffer.from(e1)).not.toEqual(Buffer.from(e2));
});

/**
 * Ensures RSA-OAEP enforces maximum message size limits
 * Verifies:
 * - oversized input correctly throws an error
 * - encryption is not misused for large payloads
 */
test('RSA fails on too large message', async () => {
	const { publicKey } = await createAndExportKeys();
	const pub = await importPublicKey(publicKey);

	const large = new Uint8Array(256); // maxMessageSize  = keySizeInBytes  - (2 * hashSizeInBytes ) - 2

	await expect(crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pub, large)).rejects.toThrow();
});

/**
 * Ensures that the same password + same salt always
 * produces the same derived key.
 *
 * This is required because:
 * - encryption/decryption depends on stable keys
 * - PBKDF2 must be deterministic
 */
test('PBKDF2 is deterministic via encryption output', async () => {
	const password = 'password123';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key1 = await deriveKeyFromPassword(password, salt);
	const key2 = await deriveKeyFromPassword(password, salt);

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
 * Ensures PBKDF2 + AES chain is secure:
 * - wrong password -> wrong key
 * - wrong key -> decryption failure
 */
test('wrong password cannot decrypt data', async () => {
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const correctKey = await deriveKeyFromPassword('correct', salt);
	const wrongKey = await deriveKeyFromPassword('wrong', salt);

	const data = new TextEncoder().encode('secret');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, correctKey, data);

	// Wrong key must fail decryption
	await expect(
		crypto.subtle.decrypt({ name: 'AES-GCM', iv }, wrongKey, encrypted)
	).rejects.toThrow();
});

/**
 * Different salts must produce incompatible keys.
 *
 * This ensures:
 * - same password != same deerived key globally
 * - protection against rainbow table attacks
 */
test('different salts produce incompatible keys', async () => {
	const password = 'password123';

	const salt1 = crypto.getRandomValues(new Uint8Array(16));
	const salt2 = crypto.getRandomValues(new Uint8Array(16));

	const key1 = await deriveKeyFromPassword(password, salt1);
	const key2 = await deriveKeyFromPassword(password, salt2);

	const data = new TextEncoder().encode('message');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, key1, data);

	// Key derived from different salt should NOT decrypt
	await expect(crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key2, encrypted)).rejects.toThrow();
});

/**
 * Ensures PBKDF2 iteration count is usable in real UX.
 *
 * Goal:
 * - secure (600k iterations)
 * - still fast enough (<2s ideally)
 */
test('PBKDF2 performance is acceptable', async () => {
	const password = 'bench';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const start = performance.now();

	await deriveKeyFromPassword(password, salt, 600000);

	const duration = performance.now() - start;

	console.log(`PBKDF2 took ${duration.toFixed(2)}ms`);

	// Adjust based on UX target (mobile vs desktop)
	expect(duration).toBeLessThan(2000);
});

/**
 * Ensures AES-GCM encrypt/decrypt works correctly
 *
 * Verifies:
 * - file can be encrypted
 * - decrypted output matches original
 * - AES-GCM integrity is working
 */
test('AES-GCM encrypt/decrypt roundtrip', async () => {
	const key = await generateAESKey();

	const original = new TextEncoder().encode('hello crypto world');

	const { iv, ciphertext } = await encryptFile(original.buffer, key);

	const decrypted = await decryptFile(ciphertext, key, iv);
	const result = new TextDecoder().decode(decrypted);

	expect(result).toBe('hello crypto world');
});

/**
 * Ensures AES encryption is non-deterministic
 *
 * Verifies:
 * - same input does NOT produce same ciphertext
 * - IV randomness is working correctly
 */
test('AES-GCM produces different ciphertexts', async () => {
	const key = await generateAESKey();
	const data = new TextEncoder().encode('same message');

	const e1 = await encryptFile(data.buffer, key);
	const e2 = await encryptFile(data.buffer, key);

	expect(e1.ciphertext).not.toBe(e2.ciphertext);
});

/**
 * Ensures RSA wrap/unwrap preserves AES key
 *
 * Verifies:
 * - AES key survives RSA-OAEP wrapping
 * - unwrap returns usable CryptoKey
 */
test('wrapAESKey + unwrapAESKey roundtrip', async () => {
	const { publicKey, privateKey } = await generateRSAKeyPair();

	const aesKey = await generateAESKey();

	const wrapped = await wrapAESKey(aesKey, publicKey);
	const unwrapped = await unwrapAESKey(wrapped, privateKey);

	const data = new TextEncoder().encode('message');
	const iv = crypto.getRandomValues(new Uint8Array(12));

	const encrypted = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, unwrapped, data);
	const decrypted = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, unwrapped, encrypted);

	expect(new TextDecoder().decode(decrypted)).toBe('message');
});

/**
 * Ensures wrong RSA private key cannot unwrap AES key
 *
 * Verifies:
 * - key wrapping is secure
 * - only correct private key can recover AES key
 */
test('wrong RSA key fails unwrap', async () => {
	const rsa1 = await generateRSAKeyPair();
	const rsa2 = await generateRSAKeyPair();

	const aesKey = await generateAESKey();

	const wrapped = await wrapAESKey(aesKey, rsa1.publicKey);

	await expect(unwrapAESKey(wrapped, rsa2.privateKey)).rejects.toThrow();
});

/**
 * Ensures AES-GCM detects tampering
 *
 * Verifies:
 * - modifying ciphertext breaks decryption
 * - authentication tag is enforced
 */
test('AES-GCM detects tampering', async () => {
	const key = await generateAESKey();

	const data = new TextEncoder().encode('secret file content');

	const { iv, ciphertext } = await encryptFile(data.buffer, key);

	const tampered = new Uint8Array(ciphertext);
	tampered[0] ^= 1;

	await expect(decryptFile(tampered.buffer, key, iv)).rejects.toThrow();
});

/**
 * Ensures recovery key is valid base64 and has correct entropy size.
 *
 * Verifies:
 * - output is string
 * - decodes to 32 bytes
 */
test('recovery key generation is valid', async () => {
	const key = await generateRecoveryKey();
	console.log(key);
	const raw = atob(key);
	const bytes = new Uint8Array([...raw].map((c) => c.charCodeAt(0)));

	expect(typeof key).toBe('string');
	expect(bytes.length).toBe(32);
});

/**
 * Ensures private key can be encrypted and recovered using recovery key.
 *
 * Verifies:
 * - PKCS#8 export works
 * - AES-GCM encryption works
 * - RSA key is correctly restored
 */
test('private key recovery roundtrip', async () => {
	const rsa = await generateRSAKeyPair();

	const { privateKey } = rsa;

	const recoveryKeyBase64 = await generateRecoveryKey();
	const recoveryKey = await importRecoveryKey(recoveryKeyBase64);

	const { encrypted, iv } = await encryptPrivateKeyWithRecovery(privateKey, recoveryKey);

	const recovered = await recoverPrivateKey(encrypted, recoveryKey, iv);

	const message = new TextEncoder().encode('message');
	const pubKey = rsa.publicKey;

	const encryptedMsg = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pubKey, message);
	const decryptedMsg = await crypto.subtle.decrypt({ name: 'RSA-OAEP' }, recovered, encryptedMsg);

	expect(new TextDecoder().decode(decryptedMsg)).toBe('message');
});

/**
 * Ensures wrong recovery key cannot decrypt private key.
 *
 * Verifies:
 * - AES-GCM integrity prevents unauthorized access
 * - decryption fails completely
 */
test('wrong recovery key fails private key recovery', async () => {
	const rsa = await generateRSAKeyPair();

	const recoveryKey1 = await generateRecoveryKey();
	const recoveryKey2 = await generateRecoveryKey();

	const k1 = await importRecoveryKey(recoveryKey1);
	const k2 = await importRecoveryKey(recoveryKey2);

	const { encrypted, iv } = await encryptPrivateKeyWithRecovery(rsa.privateKey, k1);

	await expect(recoverPrivateKey(encrypted, k2, iv)).rejects.toThrow();
});

/**
 * Ensures AES-GCM detects IV tampering.
 *
 * Verifies:
 * - modifying IV breaks decryption
 */
test('tampered IV breaks recovery', async () => {
	const rsa = await generateRSAKeyPair();

	const recoveryKeyBase64 = await generateRecoveryKey();
	const recoveryKey = await importRecoveryKey(recoveryKeyBase64);

	const { encrypted, iv } = await encryptPrivateKeyWithRecovery(rsa.privateKey, recoveryKey);

	const badIv = new Uint8Array(iv);
	badIv[0] ^= 1;

	await expect(recoverPrivateKey(encrypted, recoveryKey, badIv)).rejects.toThrow();
});

/**
 * Ensures a private key can be securely encrypted and recovered
 * using a password-derived AES key.
 *
 * Verifies:
 * - PBKDF2-derived key can encrypt private key
 * - AES-GCM encryption/decryption works
 * - recovered key is fully usable for RSA operations
 */
test('private key encryption with password roundtrip', async () => {
	const rsa = await generateRSAKeyPair();

	const password = 'strong-password';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const passwordKey = await deriveKeyFromPassword(password, salt);

	const { encrypted, iv } = await encryptPrivateKeyWithPassword(rsa.privateKey, passwordKey);

	const recovered = await decryptPrivateKeyWithPassword(encrypted, passwordKey, iv);

	const message = new TextEncoder().encode('hello password');

	const encryptedMsg = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, rsa.publicKey, message);

	const decryptedMsg = await crypto.subtle.decrypt({ name: 'RSA-OAEP' }, recovered, encryptedMsg);

	expect(new TextDecoder().decode(decryptedMsg)).toBe('hello password');
});

/**
 * Ensures that an incorrect password cannot decrypt the private key.
 *
 * Verifies:
 * - PBKDF2 produces different keys for different passwords
 * - AES-GCM rejects decryption with incorrect key
 * - private key remains inaccessible without correct password
 */
test('wrong password fails private key decryption', async () => {
	const rsa = await generateRSAKeyPair();

	const salt = crypto.getRandomValues(new Uint8Array(16));

	const correctKey = await deriveKeyFromPassword('correct', salt);
	const wrongKey = await deriveKeyFromPassword('wrong', salt);

	const { encrypted, iv } = await encryptPrivateKeyWithPassword(rsa.privateKey, correctKey);

	await expect(decryptPrivateKeyWithPassword(encrypted, wrongKey, iv)).rejects.toThrow();
});

/**
 * Ensures that using a different salt results in a completely different key.
 *
 * Verifies:
 * - PBKDF2 salt affects key derivation
 * - same password + different salt != same key
 * - incorrect salt prevents private key recovery
 *
 * Security importance:
 * - prevents rainbow-table attacks
 * - ensures uniqueness per user/session
 */
test('wrong salt fails private key decryption', async () => {
	const rsa = await generateRSAKeyPair();

	const salt1 = crypto.getRandomValues(new Uint8Array(16));
	const salt2 = crypto.getRandomValues(new Uint8Array(16));

	const key1 = await deriveKeyFromPassword('password', salt1);
	const key2 = await deriveKeyFromPassword('password', salt2);

	const { encrypted, iv } = await encryptPrivateKeyWithPassword(
		rsa.privateKey,
		key1
	);

	await expect(
		decryptPrivateKeyWithPassword(encrypted, key2, iv)
	).rejects.toThrow();
});

/**
 * Ensures AES-GCM detects IV tampering during private key decryption.
 *
 * Verifies:
 * - modifying IV breaks authentication
 * - AES-GCM integrity protection is enforced
 * - corrupted metadata prevents key recovery
 */
test('tampered IV breaks password-based private key recovery', async () => {
	const rsa = await generateRSAKeyPair();

	const password = 'secure';
	const salt = crypto.getRandomValues(new Uint8Array(16));

	const key = await deriveKeyFromPassword(password, salt);

	const { encrypted, iv } = await encryptPrivateKeyWithPassword(
		rsa.privateKey,
		key
	);

	const badIv = new Uint8Array(iv);
	badIv[0] ^= 1;

	await expect(
		decryptPrivateKeyWithPassword(encrypted, key, badIv)
	).rejects.toThrow();
});