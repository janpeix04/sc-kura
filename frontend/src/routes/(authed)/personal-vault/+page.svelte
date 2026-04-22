<script lang="ts">
	import FileTable from '$lib/components/FileTable.svelte';
	import PersonalVaultDialog from '$lib/components/PersonalVaultDialog.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { onMount, setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);

	let folders = $derived(data.folders ?? []);
	let files = $derived(data.files ?? []);

	let openDialog = $state(false);

	onMount(() => {
		/* TOOD: check if is this the first time user access Personal Vault */
		openDialog = true;
	});
</script>

{#snippet children()}
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
{/snippet}

<StorageLayout
	user={data.user}
	folderId={data.root!.id}
	availableSpace={data.availableSpace}
	{children}
/>

<PersonalVaultDialog bind:open={openDialog} />
