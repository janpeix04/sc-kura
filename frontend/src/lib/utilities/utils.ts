import { invalidate } from '$app/navigation';
import { page } from '$app/state';
import {
	cryptoDownloadFileFileIdGet,
	type EncryptedFilePublic,
	type EncryptedFolderPublic,
	type EncryptedFolderTree
} from '$lib/client';
import { base64ToArrayBuffer, decryptFile, unwrapKey } from '$lib/crypto';
import { m } from '$lib/paraglide/messages';
import { getLocale } from '$lib/paraglide/runtime';
import type {
	DecryptedFile,
	DecryptedFileNode,
	DecryptedFolder,
	DecryptedFolderNode
} from '$lib/schemas/types';
import { toast } from 'svelte-sonner';
import { clientSideClient } from './client-side';
import JSZip from 'jszip';

export function getUserInitials(firstName: string, lastName: string) {
	const firstInitial = firstName[0].toUpperCase();
	const lastInitial = lastName[0].toUpperCase();
	return firstInitial + lastInitial;
}

export function capitalize(text: string) {
	return text[0].toUpperCase() + text.slice(1);
}

export function formatBytes(bytes: number, decimals: number = 2) {
	if (bytes === 0) return '0 B';

	const k = 1024;
	const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));

	const value = bytes / Math.pow(k, i);
	const formatted = Number.isInteger(value) ? value.toString() : value.toFixed(decimals);

	return `${formatted} ${sizes[i]}`;
}

export function formatDate(date: string) {
	const d = new Date(date);

	return d.toLocaleDateString(getLocale(), {
		month: 'short',
		day: 'numeric',
		year: 'numeric'
	});
}

export function invalidatePage() {
	const pathname = page.url.pathname;

	if (pathname.includes('home')) {
		invalidate('data:home');
	}

	if (pathname.includes('folder')) {
		invalidate('data:folder');
	}

	if (pathname.includes('my-files')) {
		invalidate('data:my-files');
	}

	if (pathname.includes('trash')) {
		invalidate('data:trash');
	}

	if (pathname.includes('personal-vault')) {
		invalidate('data:personal-vault');
	}
}

export async function decryptFolder(folder: EncryptedFolderPublic, privateKey: CryptoKey) {
	const wrappedKey = base64ToArrayBuffer(folder.encrypted_key);
	const key = await unwrapKey(wrappedKey, privateKey);

	const encryptedNameBuffer = base64ToArrayBuffer(folder.encrypted_name);
	const iv = base64ToArrayBuffer(folder.iv);

	const encodedName = await decryptFile(key, iv, encryptedNameBuffer);
	const name = new TextDecoder().decode(encodedName);

	return {
		id: folder.id,
		key,
		name,
		type: folder.type ?? 'directory',
		size: folder.size,
		createdAt: folder.created_at,
		parentId: folder.parent_id
	} as DecryptedFolder;
}

export async function decryptFilePublic(file: EncryptedFilePublic, privateKey: CryptoKey) {
	const wrappedKey = base64ToArrayBuffer(file.encrypted_key);
	const key = await unwrapKey(wrappedKey, privateKey);

	const encryptedNameBuffer = base64ToArrayBuffer(file.encrypted_name);
	const iv = base64ToArrayBuffer(file.encrypted_name_iv);

	const encodedName = await decryptFile(key, iv, encryptedNameBuffer);
	const name = new TextDecoder().decode(encodedName);

	return {
		id: file.id,
		key,
		name,
		type: m.file(),
		size: file.size,
		createdAt: file.created_at,
		parentId: file.parent_id
	} as DecryptedFile;
}

export async function decryptCollection<TEncrypted, TDecrypted>({
	items,
	decrypt,
	assign,
	errorMessage
}: {
	items: TEncrypted[];
	decrypt: (item: TEncrypted) => Promise<TDecrypted>;
	assign: (items: TDecrypted[]) => void;
	errorMessage: string;
}) {
	if (!items.length) {
		assign([]);
		return;
	}

	try {
		const results = await Promise.all(items.map(decrypt));
		assign(results);
	} catch (err) {
		console.error(errorMessage, err);
	}
}

export async function downloadAndDecryptFile(fileId: string, privateKey: CryptoKey) {
	const { data, error, response } = await cryptoDownloadFileFileIdGet({
		client: clientSideClient,
		path: {
			file_id: fileId
		}
	});

	if (error) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const wrappedKey = response.headers.get('x-encrypted-key');
	const fileIv = response.headers.get('x-iv');
	const encryptedName = response.headers.get('x-encrypted-name');
	const encryptedNameIv = response.headers.get('x-encrypted-name-iv');

	if (
		wrappedKey === null ||
		fileIv === null ||
		encryptedName === null ||
		encryptedNameIv === null
	) {
		toast.error(m.oops_something_went_wrong());
		return;
	}

	const wrappedKeyBuffer = base64ToArrayBuffer(wrappedKey);
	const key = await unwrapKey(wrappedKeyBuffer, privateKey);

	const encryptedBuffer = await data.arrayBuffer();
	const iv = base64ToArrayBuffer(fileIv);

	const decryptedBuffer = await decryptFile(key, iv, encryptedBuffer);
	const blob = new Blob([decryptedBuffer]);

	const encryptedNameBuffer = base64ToArrayBuffer(encryptedName);
	const nameIv = base64ToArrayBuffer(encryptedNameIv);

	const encodedName = await decryptFile(key, nameIv, encryptedNameBuffer);
	const filename = new TextDecoder().decode(encodedName);

	return {
		id: fileId,
		name: filename,
		blob
	} as DecryptedFileNode;
}

export async function decryptFolderName(folder: EncryptedFolderTree, privateKey: CryptoKey) {
	const wrappedKey = base64ToArrayBuffer(folder.encrypted_key);
	const key = await unwrapKey(wrappedKey, privateKey);

	const encryptedName = base64ToArrayBuffer(folder.encrypted_name);
	const iv = base64ToArrayBuffer(folder.iv);

	const decrypted = await decryptFile(key, iv, encryptedName);

	return {
		name: new TextDecoder().decode(decrypted),
		key
	};
}

export async function decryptFolderTree(
	folder: EncryptedFolderTree,
	privateKey: CryptoKey
): Promise<DecryptedFolderNode> {
	const decryptedFolder = await decryptFolderName(folder, privateKey);

	const files = await Promise.all(
		(folder.files ?? []).map((file) => downloadAndDecryptFile(file.id, privateKey))
	);

	const folders = await Promise.all(
		(folder.folders ?? []).map((child) => decryptFolderTree(child, privateKey))
	);

	return {
		id: folder.id,
		name: decryptedFolder.name,
		files,
		folders
	} as DecryptedFolderNode;
}

export async function buildZipFromTree(root: DecryptedFolderNode) {
	const zip = new JSZip();

	await addFolderToZip(zip, root, '');
	const blob = await zip.generateAsync({ type: 'blob' });

	return blob;
}

async function addFolderToZip(zip: JSZip, node: DecryptedFolderNode, path: string) {
	const currentPath = path ? `${path}/${node.name}` : node.name;

	const folder = zip.folder(currentPath);

	if (!folder) return;

	for (const file of node.files ?? []) {
		folder.file(file.name, file.blob);
	}

	for (const child of node.folders) {
		await addFolderToZip(zip, child, currentPath);
	}
}
