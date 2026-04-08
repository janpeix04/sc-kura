<script lang="ts">
	import type { Breadcrumbs } from '$lib/client/types.gen.js';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import Folder from '$lib/components/Folder.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let breadcrumbs = $derived(data.breadcrumbs as Breadcrumbs[]);
	let folders = $derived(data.folders);
</script>

{#snippet children()}
	<Breadcrumb {breadcrumbs} />

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

<StorageLayout user={data.user} {children} />
