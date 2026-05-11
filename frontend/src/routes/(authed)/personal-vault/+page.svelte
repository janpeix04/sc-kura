<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import PersonalVaultDialog from '$lib/components/PersonalVaultDialog.svelte';
	import PersonalVaultLoginDialog from '$lib/components/PersonalVaultLoginDialog.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { vault } from '$lib/stores/vault';
	import { onMount } from 'svelte';
	import { privateKey } from '$lib/stores/crypto.js';
	import { get } from 'svelte/store';
	import type { DecryptedFile, DecryptedFolder } from '$lib/schemas/types.js';
	import EncryptedFileTable from '$lib/components/EncryptedFileTable.svelte';
	import { decryptCollection, decryptFilePublic, decryptFolder } from '$lib/utilities/utils.js';

	let { data } = $props();

	let showFirstTime = $state(false);

	let folders: DecryptedFolder[] = $state([]);
	let files: DecryptedFile[] = $state([]);

	async function decryptVault(privateKey: CryptoKey) {
		await Promise.all([
			decryptCollection({
				items: data.folders ?? [],
				decrypt: (folder) => decryptFolder(folder, privateKey),
				assign: (result) => (folders = result),
				errorMessage: m.oops_something_went_wrong()
			}),
			decryptCollection({
				items: data.files ?? [],
				decrypt: (file) => decryptFilePublic(file, privateKey),
				assign: (result) => (files = result),
				errorMessage: m.oops_something_went_wrong()
			})
		]);
	}

	onMount(() => {
		if (!data.hasSeen) {
			showFirstTime = true;
			$vault.locked = true;
			return;
		}

		if (data.hasSeen && !$vault.token) {
			$vault.locked = true;
		}
	});

	$effect(() => {
		const expiresAt = $vault.expiresAt;

		if (!expiresAt) return;

		const remaining = expiresAt - Date.now();

		if (remaining <= 0) {
			$vault.locked = true;
			$vault.token = null;
			$vault.expiresAt = null;
			return;
		}

		const timer = setTimeout(() => {
			$vault.locked = true;
			$vault.token = null;
			$vault.expiresAt = null;
		}, remaining);

		return () => clearTimeout(timer);
	});

	$effect(() => {
		if (!data.hasSeen) return;

		const priv = get(privateKey);
		const encryptedFolders = data.folders;

		if (!encryptedFolders || encryptedFolders.length === 0 || !priv) return;

		Promise.all(encryptedFolders.map((folder) => decryptFolder(folder, priv)))
			.then((results) => (folders = results))
			.catch((err) => console.error('Failed to decrypt folders:', err));
	});

	$effect(() => {
		if (!data.hasSeen) return;

		const priv = get(privateKey);

		if (!priv) return;

		decryptVault(priv);
	});
</script>

{#if showFirstTime}
	<PersonalVaultDialog open={showFirstTime} user={data.user} updateUserForm={data.updateUserForm} />
{:else if $vault.locked}
	<PersonalVaultLoginDialog
		open={!showFirstTime}
		verifyPasswordForm={data.verifyPasswordForm}
		resetPasswordForm={data.resetPasswordForm}
		cb={async (privateKey: CryptoKey) => {
			const encryptedFolders = data.folders;

			if (!encryptedFolders || encryptedFolders.length === 0) return;

			await decryptVault(privateKey);
		}}
	/>
{/if}

<StorageLayout
	user={data.user}
	folderId={data.folderId}
	availableSpace={data.availableSpace}
	isEncrypted
>
	<Breadcrumb.Root>
		<Breadcrumb.List class="text-lg text-foreground">
			<Breadcrumb.Item>
				<span class="text-2xl">{m.personal_vault()}</span>
			</Breadcrumb.Item>
		</Breadcrumb.List>
	</Breadcrumb.Root>

	{#if folders?.length || files?.length}
		<EncryptedFileTable bind:folders bind:files location={m.personal_vault()} />
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
</StorageLayout>
