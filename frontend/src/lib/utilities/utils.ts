import { invalidate } from '$app/navigation';
import { page } from '$app/state';
import type { EncryptedFilePublic, EncryptedFolderPublic } from '$lib/client';
import { base64ToArrayBuffer, decryptFile, unwrapKey } from '$lib/crypto';
import { m } from '$lib/paraglide/messages';
import { getLocale } from '$lib/paraglide/runtime';
import type { DecryptedFile, DecryptedFolder } from '$lib/schemas/types';

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
