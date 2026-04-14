<script lang="ts">
	import Folder from '$lib/components/Folder.svelte';
	import * as Collapsible from '$lib/components/ui/collapsible/index.js';
	import ItemsListLayout from '$lib/layouts/ItemsListLayout.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let suggestedFoldersOpen = $state(true);
	let suggestedFilesOpen = $state(true);

	let suggestedFolders = $state(data.suggestedFolders);
	let suggestedFiles = $state(data.suggestedFiles);
</script>

{#snippet children()}
	<div class="flex flex-col gap-4">
		<Collapsible.Root bind:open={suggestedFoldersOpen}>
			<Collapsible.Trigger
				class="flex cursor-pointer items-center gap-4 rounded-full px-4 py-1 hover:bg-selected hover:text-on-selected"
			>
				<span
					class="icon-[lucide--chevron-down] size-5 transition-transform duration-200"
					class:-rotate-90={!suggestedFoldersOpen}
				></span>
				{m.suggested_folders()}
			</Collapsible.Trigger>
			<Collapsible.Content>
				<div class="mt-2 flex flex-nowrap gap-2 overflow-hidden px-4">
					{#each suggestedFolders as folder (folder.id)}
						<Folder {folder} compact={true} />
					{/each}
				</div>
			</Collapsible.Content>
		</Collapsible.Root>

		<Collapsible.Root bind:open={suggestedFilesOpen}>
			<Collapsible.Trigger
				class="flex cursor-pointer items-center gap-4 rounded-full px-4 py-1 hover:bg-selected hover:text-on-selected"
			>
				<span
					class="icon-[lucide--chevron-down] size-5 transition-transform duration-200"
					class:-rotate-90={!suggestedFilesOpen}
				></span>
				{m.suggested_files()}
			</Collapsible.Trigger>

			<Collapsible.Content class="px-4">
				<ItemsListLayout bind:files={suggestedFiles} />
			</Collapsible.Content>
		</Collapsible.Root>
	</div>
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.root!.id} />
