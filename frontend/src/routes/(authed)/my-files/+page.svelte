<script lang="ts">
	import ItemGrid from '$lib/components/ItemGrid.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let folders = $derived(data.folders);
	let files = $derived(data.files)
</script>

{#snippet children()}
	<Breadcrumb.Root>
		<Breadcrumb.List class="text-lg">
			<Breadcrumb.Item>
				<Breadcrumb.Link href={localizeHref('/my-files')}>
					<span class="text-2xl">{m.my_files()}</span>
				</Breadcrumb.Link>
			</Breadcrumb.Item>
			<Breadcrumb.Separator class="flex" />
		</Breadcrumb.List>
	</Breadcrumb.Root>

	<ItemGrid bind:folders bind:files />
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.folderId} />
