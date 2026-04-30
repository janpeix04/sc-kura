import { invalidate } from '$app/navigation';
import { page } from '$app/state';
import { getLocale } from '$lib/paraglide/runtime';

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
