import { invalidate } from '$app/navigation';
import { storageAvailableSpaceGet } from '$lib/client';
import { createClient } from '$lib/client/client';
import { STORAGE_STATUS } from '$lib/schemas/types';
import { availableSpace } from '$lib/stores/storage';

const client = createClient({ baseUrl: '' });

export function formatBytes(bytes: number, decimals: number = 2): string {
	if (bytes === 0) return '0 B';

	const k = 1024;
	const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));

	const value = bytes / Math.pow(k, i);

	return `${value.toFixed(decimals)} ${sizes[i]}`;
}

export function get_path(path: string | undefined): string {
	if (path === undefined || path === '/') return '-';
	return path.slice(1).replaceAll('/', '-');
}

export function invalidatePages(pathname: string) {
	if (pathname.startsWith('/storage/folder')) {
		invalidate('data:folder');
	}
	if (pathname.startsWith('/storage/home')) {
		invalidate('data:storage-home');
	}
	if (pathname.startsWith('/storage/my-files')) {
		invalidate('data:my-files');
	}
	if (pathname.startsWith('/storage/trash')) {
		invalidate('data:trash');
	}
}

export function downloadBlob(blob: Blob, itemName: string) {
	const url = window.URL.createObjectURL(blob);
	const a = document.createElement('a');
	a.href = url;
	a.download = itemName;
	document.body.appendChild(a);
	a.click();
	a.remove();
	window.URL.revokeObjectURL(url);
}

export function parseStorageFolderId(value: string) {
	const lastDashIndex = value.lastIndexOf('-');

	const folderId = value.substring(0, lastDashIndex);
	const status = value.substring(lastDashIndex + 1);

	return { folderId, status };
}

export function getStorageStatus(value: string) {
	switch (value) {
		case STORAGE_STATUS.DELETED:
			return 'deleted';
		default:
			return 'uploaded';
	}
}

export async function updateStorageAvailableSpace() {
	const { data } = await storageAvailableSpaceGet({
		client,
		throwOnError: true
	});

	availableSpace.set(data);
}