<script lang="ts">
	import type { CryptoBreadcrumbs } from '$lib/client/types.gen.js';
	import EncryptedBreadcrumb from '$lib/components/EncryptedBreadcrumb.svelte';
	import EncryptedFileTable from '$lib/components/EncryptedFileTable.svelte';
	import { base64ToArrayBuffer, decryptFile, decryptFolder, unwrapKey } from '$lib/crypto.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { DecryptedBreadcrumb, DecryptedFolder } from '$lib/schemas/types.js';
	import { privateKey } from '$lib/stores/crypto.js';
	import { vault } from '$lib/stores/vault.js';
	import { get } from 'svelte/store';

	let { data } = $props();

	let breadcrumbs: DecryptedBreadcrumb[] = $state([]);
	let folders: DecryptedFolder[] = $state([]);

	async function decryptBreadcrumbs(privateKey: CryptoKey, breadcrumb: CryptoBreadcrumbs) {
		const wrappedKey = base64ToArrayBuffer(breadcrumb.folder_encrypted_key);
		const key = await unwrapKey(wrappedKey, privateKey);

		const encryptedName = base64ToArrayBuffer(breadcrumb.folder_encrypted_name);
		const iv = base64ToArrayBuffer(breadcrumb.folder_iv);

		const encodedName = await decryptFile(key, iv, encryptedName);

		return {
			folder_id: breadcrumb.folder_id,
			name: new TextDecoder().decode(encodedName)
		} as DecryptedBreadcrumb;
	}

	$effect(() => {
		if ($vault.locked) return;

		const priv = get(privateKey);
		const encryptedFolders = data.folders;

		if (!encryptedFolders || !priv) return;

		if (encryptedFolders.length === 0) {
			folders = [];
		}

		Promise.all(encryptedFolders.map((folder) => decryptFolder(folder, priv)))
			.then((results) => (folders = results))
			.catch((err) => console.error('Failed to decrypt folders:', err));
	});

	$effect(() => {
		if ($vault.locked) return;

		const priv = get(privateKey);
		const encryptedBreadcrumb = data.breadcrumbs;

		if (!encryptedBreadcrumb || encryptedBreadcrumb.length === 0 || !priv) return;

		Promise.all(encryptedBreadcrumb.map((b) => decryptBreadcrumbs(priv, b)))
			.then((results) => (breadcrumbs = results))
			.catch((err) => console.error('Failed to decrypt folders:', err));
	});
</script>

{#snippet children()}
	<EncryptedBreadcrumb {breadcrumbs} />

	{#if folders?.length}
		<EncryptedFileTable bind:folders location="TODO" />
	{:else}
		<div class="flex h-full flex-col items-center justify-center gap-2 text-center">
			<span class="icon-[lucide--folder] size-32 text-muted-foreground"></span>

			<span class="text-lg font-medium">
				{m.empty_folder_title()}
			</span>

			<span class=" text-sm text-muted-foreground">
				{m.empty_folder_description()}
			</span>
		</div>
	{/if}
{/snippet}

<StorageLayout
	user={data.user}
	{children}
	folderId={data.folderId}
	availableSpace={data.availableSpace!}
/>
