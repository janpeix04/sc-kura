<script lang="ts">
	import StorageLayout from "$lib/layouts/StorageLayout.svelte";

	let { data } = $props();
</script>

{#snippet children()}
	test
{/snippet}

<StorageLayout user={data.user} {children} />
