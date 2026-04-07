<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import type { UserPublic } from '$lib/client';
	import Nav from '$lib/components/Nav.svelte';
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { m } from '$lib/paraglide/messages';

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
			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					<Button>
						<span class="icon-[lucide--plus] size-4"></span>
						{m.new()}
					</Button>
				</DropdownMenu.Trigger>
				<DropdownMenu.Content class="w-fit">
					<DropdownMenu.Item class="cursor-pointer">
						<span class="icon-[lucide--folder-plus] size-4"></span>
						{m.new_folder()}
					</DropdownMenu.Item>
					<DropdownMenu.Separator />
					<DropdownMenu.Item class="cursor-pointer">
						<span class="icon-[lucide--file-plus] size-4"></span>
						{m.file_upload()}
					</DropdownMenu.Item>
					<DropdownMenu.Item class="cursor-pointer">
						<span class="icon-[lucide--folder-up] size-4"></span>
						{m.folder_upload()}
					</DropdownMenu.Item>
				</DropdownMenu.Content>
			</DropdownMenu.Root>
		</aside>

		<main class="flex-1 overflow-auto pr-4 pb-6">
			<div class="h-full w-full rounded-2xl bg-white p-6">
				{@render children()}
			</div>
		</main>
	</div>
</div>
