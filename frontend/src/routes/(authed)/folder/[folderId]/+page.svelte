<script lang="ts">
	import type { Breadcrumbs } from '$lib/client/types.gen.js';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import Folder from '$lib/components/Folder.svelte';
	import ItemGrid from '$lib/components/ItemGrid.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
	import { m } from '$lib/paraglide/messages.js';
	import { setContext } from 'svelte';

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
	setContext('renameItemForm', data.renameItemForm);

	let breadcrumbs = $derived(data.breadcrumbs as Breadcrumbs[]);
	let folders = $derived(data.folders);
	let files = $derived(data.files);
</script>

{#snippet children()}
	<Breadcrumb {breadcrumbs} />
	<ItemGrid bind:folders bind:files />
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.folderId} />
