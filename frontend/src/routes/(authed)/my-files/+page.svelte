<script lang="ts">
	import FileTable from '$lib/components/FileTable.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import { ScrollArea } from '$lib/components/ui/scroll-area/index.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);

	let folders = $derived(data.folders);
	let files = $derived(data.files);
</script>

{#snippet children()}
	<Breadcrumb.Root>
		<Breadcrumb.List class="text-lg text-foreground">
			<Breadcrumb.Item>
				<span class="text-2xl">{m.my_files()}</span>
			</Breadcrumb.Item>
		</Breadcrumb.List>
	</Breadcrumb.Root>

	<ScrollArea class="h-full w-full py-4">
		<FileTable bind:folders bind:files />
	</ScrollArea>
{/snippet}

<StorageLayout
	user={data.user}
	{children}
	folderId={data.folderId}
	availableSpace={data.availableSpace!}
/>
