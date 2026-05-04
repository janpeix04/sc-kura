<script lang="ts">
	import type { CryptoBreadcrumbs } from '$lib/client/types.gen.js';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import EncryptedFileTable from '$lib/components/EncryptedFileTable.svelte';
	import { decryptFolder } from '$lib/crypto.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { DecryptedFolder } from '$lib/schemas/types.js';
	import { privateKey } from '$lib/stores/crypto.js';
	import { vault } from '$lib/stores/vault.js';
	import { get } from 'svelte/store';

	let { data } = $props();

	let breadcrumbs = $derived(data.breadcrumbs as CryptoBreadcrumbs[]);
	let folders: DecryptedFolder[] = $state([]);

	$effect(() => {
		if ($vault.locked) return;

		const priv = get(privateKey);
		const encryptedFolders = data.folders;

		if (!encryptedFolders || encryptedFolders.length === 0 || !priv) return;

		Promise.all(encryptedFolders.map((folder) => decryptFolder(folder, priv)))
			.then((results) => (folders = results))
			.catch((err) => console.error('Failed to decrypt folders:', err));
	});
</script>

{#snippet children()}
	<!-- <Breadcrumb {breadcrumbs} /> -->

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
