<script lang="ts">
	import type { UserPublic } from '$lib/client';
	import Nav from '$lib/components/Nav.svelte';
	import Button from '$lib/components/ui/button/button.svelte';
	import type { Snippet } from 'svelte';

	let {
		user,
		children
	}: {
		user: UserPublic;
		children: Snippet;
	} = $props();
</script>

<div class="flex h-screen w-full flex-col">
	<Nav {user} />
	<div class="flex flex-1 overflow-hidden">
		<aside class="w-72 shrink-0 px-4 py-4">
			<Button>
				<span class="icon-[lucide--plus] size-4"></span>
				New
			</Button>
		</aside>

		<main class="flex-1 overflow-auto pt-1 pr-4 pb-4">
			<div class="h-full w-full rounded-2xl bg-white p-6">
				{@render children()}
			</div>
		</main>
	</div>
</div>
