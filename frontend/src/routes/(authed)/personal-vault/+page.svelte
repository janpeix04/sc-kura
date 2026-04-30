<script lang="ts">
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import PersonalVaultDialog from '$lib/components/PersonalVaultDialog.svelte';
	import PersonalVaultLoginDialog from '$lib/components/PersonalVaultLoginDialog.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { vault } from '$lib/stores/vault';
	import { onMount } from 'svelte';
	import FileTable from '$lib/components/FileTable.svelte';

	let { data } = $props();

	let showFirstTime = $state(false);

	let folders = $derived([]);
	let files = $derived([]);

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
		console.log(data.folders);
	});

	$effect(() => {
		$effect(() => {
			'called';
		});
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
</script>

{#if showFirstTime}
	<PersonalVaultDialog open={showFirstTime} user={data.user} updateUserForm={data.updateUserForm} />
{:else if $vault.locked}
	<PersonalVaultLoginDialog open={!showFirstTime} verifyPasswordForm={data.verifyPasswordForm} />
{/if}

<StorageLayout user={data.user} folderId={data.folderId} availableSpace={data.availableSpace}>
	<Breadcrumb.Root>
		<Breadcrumb.List class="text-lg text-foreground">
			<Breadcrumb.Item>
				<span class="text-2xl">{m.personal_vault()}</span>
			</Breadcrumb.Item>
		</Breadcrumb.List>
	</Breadcrumb.Root>

	{#if folders?.length || files?.length}
		<FileTable bind:folders bind:files />
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
