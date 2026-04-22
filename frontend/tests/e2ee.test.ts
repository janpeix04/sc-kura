import { generateRSAKeyPair } from '$lib/e2ee';
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
