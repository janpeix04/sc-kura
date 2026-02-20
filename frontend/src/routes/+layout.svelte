<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { Toaster } from '$lib/components/ui/sonner/index';
	import Header from '$lib/components/Header.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import AppSidebar from '$lib/components/AppSidebar.svelte';
	import { page } from '$app/state';

	let { data, children } = $props();
	let isStoragePage = $derived(page.url.pathname.startsWith('/storage'));
</script>

<Toaster position="top-center" richColors closeButton />
<Header />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="flex h-screen w-full flex-col overflow-hidden">
	<Sidebar.Provider>
		{#if isStoragePage}
			<AppSidebar user={data.user} />
		{/if}
		<Sidebar.Inset class="flex flex-1 flex-col overflow-hidden">
			<main class="flex flex-1 flex-col overflow-hidden">
				{@render children()}
			</main>
		</Sidebar.Inset>
	</Sidebar.Provider>
</div>
