<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<div class="h-screen w-full flex flex-col">
	<main class="flex-1">
		{@render children()}
	</main>
</div>
