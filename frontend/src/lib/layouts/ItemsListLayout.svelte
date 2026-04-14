<script lang="ts">
	import * as Grid from '$lib/components/ui/grid/index.js';
	import type { FilePublic, FolderPublic } from '$lib/client';
	import { goto } from '$app/navigation';
	import { localizeHref } from '$lib/paraglide/runtime';
	import ActionsButton from '$lib/components/ActionsButton.svelte';

	let {
		folders = $bindable(),
		files = $bindable()
	}: {
		folders?: FolderPublic[];
		files?: FilePublic[];
	} = $props();
</script>

<Grid.Root>
	<Grid.Header bind:folders bind:files />
	{#each folders as folder (folder.id)}
		<Grid.Row item={folder} onClick={() => goto(localizeHref(`/folder/${folder.id}`))}>
			{#snippet actions()}
				<ActionsButton item={folder} />
			{/snippet}
		</Grid.Row>
	{/each}

	{#each files as file (file.id)}
		<Grid.Row item={file}>
			{#snippet actions()}
				<ActionsButton item={file} />
			{/snippet}
		</Grid.Row>
	{/each}
</Grid.Root>
