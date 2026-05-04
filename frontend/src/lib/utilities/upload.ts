import { cryptoUploadFileFolderIdPost, storageUploadFolderIdPost } from '$lib/client';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import { m } from '$lib/paraglide/messages';
import { get } from 'svelte/store';
import { publicKey } from '$lib/stores/crypto';
import { arrayBufferToBase64, encryptFile, generateAESKey, wrapKey } from '$lib/crypto';

export async function uploadFiles(files: FileList, parentId: string, isEncrypted: boolean = false) {
	const uploads = [];

	for (const file of files) {
		if (isEncrypted) {
			uploads.push(uploadEncryptedFile(file, parentId));
		} else {
			uploads.push(uploadFile(file, parentId));
		}
	}

	return Promise.all(uploads);
}

async function uploadFile(file: File, parentId: string) {
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

	toast.success(data);
}

async function uploadEncryptedFile(file: File, parentId: string) {
	const pub = get(publicKey);

	if (!pub) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const key = await generateAESKey();

	const encodedName = new TextEncoder().encode(file.name);
	const { iv: encryptedNameIV, encrypted: encryptedName } = await encryptFile(
		key,
		encodedName.buffer
	);

	const filename = arrayBufferToBase64(encryptedName);

	const fileContent = await file.arrayBuffer();
	const { iv, encrypted } = await encryptFile(key, fileContent);

	const encryptedFile = new File([encrypted], filename, {
		type: 'application/octet-stream'
	});

	const encryptedKey = await wrapKey(key, pub);

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

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	toast.success(data);
}
