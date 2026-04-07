<script lang="ts">
	import StorageLayout from "$lib/layouts/StorageLayout.svelte";
	import { setContext } from "svelte";

	let { data } = $props();

	setContext('createFolderForm', data.createFolderForm);
</script>

{#snippet children()}
	test
{/snippet}

<StorageLayout user={data.user} {children} />
