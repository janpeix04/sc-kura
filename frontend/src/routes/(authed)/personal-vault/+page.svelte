<script lang="ts">
	import FileTable from '$lib/components/FileTable.svelte';
	import PersonalVaultDialog from '$lib/components/PersonalVaultDialog.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import type { UpdateUserSchema } from '$lib/schemas/user.js';
	import { onMount, setContext } from 'svelte';
	import type { SuperValidated } from 'sveltekit-superforms';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);

	const updateUserForm: SuperValidated<UpdateUserSchema> = $derived(data.updateUserForm);

	let folders = $derived(data.folders ?? []);
	let files = $derived(data.files ?? []);

	let openDialog = $state(false);

	onMount(() => {
		const user = data.user;
		if (user.has_seen_personal_vault) return;
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

<PersonalVaultDialog bind:open={openDialog} {updateUserForm} />
