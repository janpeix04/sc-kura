<script lang="ts">
	import DeleteDialog from '$lib/components/DeleteDialog.svelte';
	import FileTable from '$lib/components/FileTable.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import Button from '$lib/components/ui/button/button.svelte';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);

	let folders = $derived(data.folders);
	let files = $derived(data.files);

	let openDialog = $state(false);
</script>

{#snippet children()}
	<Breadcrumb.Root>
		<Breadcrumb.List class="text-lg text-foreground">
			<Breadcrumb.Item>
				<span class="text-2xl">{m.trash()}</span>
			</Breadcrumb.Item>
		</Breadcrumb.List>
	</Breadcrumb.Root>

	{#if folders?.length || files?.length}
		<div class="mt-2 flex items-center justify-between rounded-md bg-search-background px-4 py-2">
			<span class="text-sm text-muted-foreground">{m.trash_auto_delete_notice()}</span>

			<Button
				variant="ghost"
				class="py-5 text-empty-trash hover:rounded-full hover:bg-empty-trash-hover hover:text-empty-trash "
				onclick={() => (openDialog = true)}>{m.empty_trash()}</Button
			>
		</div>

		<ScrollArea class="h-full w-full py-4">
			<FileTable bind:folders bind:files />
		</ScrollArea>
	{:else}
		<div class="flex h-[90%] flex-col items-center justify-center gap-2 text-center">
			<span class="icon-[lucide--trash-2] size-32 text-muted-foreground"></span>

			<span class="text-lg font-medium">
				{m.trash_empty_title()}
			</span>

			<span class=" text-sm text-muted-foreground">
				{m.trash_empty_description()}
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

<DeleteDialog
	bind:isOpen={openDialog}
	title={m.empty_trash_title()}
	description={m.empty_trash_description()}
	confirm={m.empty_trash_confirm()}
/>
