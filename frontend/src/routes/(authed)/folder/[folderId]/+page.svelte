<script lang="ts">
	import type { Breadcrumbs } from '$lib/client/types.gen.js';
	import Breadcrumb from '$lib/components/Breadcrumb.svelte';
	import FileTable from '$lib/components/FileTable.svelte';
	import StorageLayout from '$lib/layouts/StorageLayout.svelte';
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
	<FileTable bind:folders bind:files />
{/snippet}

<StorageLayout user={data.user} {children} folderId={data.folderId} />
