<script lang="ts">
	import Folder from '$lib/components/Folder.svelte';
	import * as Breadcrumb from '$lib/components/ui/breadcrumb/index.js';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages';
	import { localizeHref } from '$lib/paraglide/runtime';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let folders = $derived(data.folders);
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

	<div class="mt-4 flex items-center gap-4 border-b border-gray-200 pb-2 text-sm font-semibold">
		<div class="flex-1">{m.name()}</div>
		<div class="w-48">{m.owner()}</div>
		<div class="w-36">{m.date_modified()}</div>
		<div class="w-24 text-right">{m.size()}</div>
		<div class="w-8"></div>
	</div>
	
	{#each folders as folder (folder.id)}
		<Folder {folder} />
	{/each}
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.root!.id} />
