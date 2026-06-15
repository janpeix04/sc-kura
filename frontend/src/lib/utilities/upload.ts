import { cryptoUploadFileFolderIdPost, storageUploadFolderIdPost } from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import { m } from '$lib/paraglide/messages';
import { get } from 'svelte/store';
import { publicKey } from '$lib/stores/crypto';
import { arrayBufferToBase64, encryptFile, generateAESKey, wrapKey } from '$lib/crypto';
import { formatBytes } from './utils';
import type { UploadMetrics } from '$lib/schemas/types';

export async function uploadFiles(files: FileList, parentId: string, isEncrypted: boolean = false) {
	const uploads = [];

	if (isEncrypted) {
		for (const file of files) {
			uploads.push(uploadEncryptedFile(file, parentId));
		}
	} else {
		for (const file of files) {
			uploads.push(uploadFile(file, parentId));
		}
	}

	return Promise.all(uploads);
}

async function uploadFile(file: File, parentId: string) {
	const t0 = performance.now();

	const uploadStart = performance.now();

	const { data } = await storageUploadFolderIdPost({
		client: clientSideClient,
		path: {
			folder_id: parentId
		},
		body: {
			file
		},
		throwOnError: true
	});

	const uploadEnd = performance.now();
	const totalEnd = performance.now();

	const metrics: UploadMetrics = {
		fileName: file.name,
		fileSize: file.size,
		uploadTime: uploadEnd - uploadStart,
		totalTime: totalEnd - t0
	};

	console.table(metrics);

	console.log(
		`📁 ${file.name} (${formatBytes(file.size)}) uploaded in ${metrics.totalTime.toFixed(2)} ms`
	);

	toast.success(data);
}

async function uploadEncryptedFile(file: File, parentId: string) {
	const pub = get(publicKey);

	if (!pub) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const t0 = performance.now();

	// AES key generation
	const keyStart = performance.now();
	const key = await generateAESKey();
	const keyEnd = performance.now();

	// Filename encryption
	const filenameStart = performance.now();

	const encodedName = new TextEncoder().encode(file.name);

	const {
		iv: encryptedNameIV,
		encrypted: encryptedName
	} = await encryptFile(key, encodedName.buffer);

	const filename = arrayBufferToBase64(encryptedName);

	const filenameEnd = performance.now();

	// File read
	const readStart = performance.now();
	const fileContent = await file.arrayBuffer();
	const readEnd = performance.now();

	// Content encryption
	const encryptStart = performance.now();

	const {
		iv,
		encrypted
	} = await encryptFile(key, fileContent);

	const encryptEnd = performance.now();

	// Create encrypted file
	const encryptedFile = new File(
		[encrypted],
		filename,
		{
			type: 'application/octet-stream'
		}
	);

	// RSA wrap
	const wrapStart = performance.now();

	const encryptedKey = await wrapKey(key, pub);

	const wrapEnd = performance.now();

	// Upload
	const uploadStart = performance.now();

	const { data, error } = await cryptoUploadFileFolderIdPost({
		client: clientSideClient,
		path: {
			folder_id: parentId
		},
		body: {
			file: encryptedFile
		},
		query: {
			encrypted_key: arrayBufferToBase64(encryptedKey),
			iv: arrayBufferToBase64(iv),
			encrypted_name: filename,
			encrypted_name_iv: arrayBufferToBase64(encryptedNameIV)
		}
	});

	const uploadEnd = performance.now();

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const totalEnd = performance.now();

	const metrics: UploadMetrics = {
		fileName: file.name,
		fileSize: file.size,
		readTime: readEnd - readStart,
		encryptNameTime: filenameEnd - filenameStart,
		encryptContentTime: encryptEnd - encryptStart,
		keyWrapTime: wrapEnd - wrapStart,
		uploadTime: uploadEnd - uploadStart,
		totalTime: totalEnd - t0
	};

	console.table(metrics);

	console.log(
		`📁 ${file.name} (${formatBytes(file.size)}) encrypted upload in ${metrics.totalTime.toFixed(2)} ms`
	);

	toast.success(data);
}