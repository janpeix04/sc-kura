import { createAndExportKeys, importPrivateKey, importPublicKey } from '$lib/utilities/e2ee';

async function testRSA() {
	console.log('🔐 Starting RSA test...');

	// 1. generate + export
	console.log('🧱 Generating RSA key pair...');
	const { publicKey, privateKey } = await createAndExportKeys();

	console.log('📤 Exported Public Key (base64):', publicKey.slice(0, 50) + '...');
	console.log('📤 Exported Private Key (base64):', privateKey.slice(0, 50) + '...');

	// 2. import keys back
	console.log('📥 Importing keys...');
	const pubKey = await importPublicKey(publicKey);
	const privKey = await importPrivateKey(privateKey);
	console.log('✅ Keys imported successfully');

	// 3. message
	const messageText = 'hello kura';
	const message = new TextEncoder().encode(messageText);
	console.log('✉️ Original message:', messageText);
	console.log('🔢 Message bytes:', message);

	// 4. encrypt
	console.log('🔒 Encrypting message...');
	const encrypted = await crypto.subtle.encrypt({ name: 'RSA-OAEP' }, pubKey, message);
	console.log('📦 Encrypted data (ArrayBuffer):', encrypted);
	console.log('📏 Encrypted byte length:', encrypted.byteLength);

	// 5. decrypt
	console.log('🔓 Decrypting message...');
	const decrypted = await crypto.subtle.decrypt({ name: 'RSA-OAEP' }, privKey, encrypted);
	console.log('📦 Decrypted data (ArrayBuffer):', decrypted);

	// 6. decode
	const result = new TextDecoder().decode(decrypted);
	console.log('✅ Decrypted text:', result);

	// 7. final check
	if (result === messageText) {
		console.log('🎉 SUCCESS: Decrypted message matches original');
	} else {
		console.error('❌ ERROR: Decrypted message does NOT match');
	}
}

testRSA();
