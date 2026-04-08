<script lang="ts">
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index';
	import type { UserPublic } from '$lib/client';
	import Nav from '$lib/components/Nav.svelte';
	import type { Snippet } from 'svelte';
	import { Button } from '$lib/components/ui/button';
	import { m } from '$lib/paraglide/messages';
	import Progress from '$lib/components/ui/progress/progress.svelte';
	import NewFolderDialog from '$lib/components/NewFolderDialog.svelte';
	import { localizeHref } from '$lib/paraglide/runtime';

	let {
		user,
		children
	}: {
		user: UserPublic;
		children: Snippet;
	} = $props();

	let createFolder = $state(false);
</script>

<div class="flex h-screen w-full flex-col">
	<Nav {user} />
	<div class="flex flex-1 overflow-hidden">
		<aside class="w-72 shrink-0 px-4 py-4">
			<DropdownMenu.Root>
				<DropdownMenu.Trigger>
					<Button class="px-4 py-2">
						<span class="icon-[lucide--plus] size-5"></span>
						{m.new()}
					</Button>
				</DropdownMenu.Trigger>
				<DropdownMenu.Content class="w-fit">
					<DropdownMenu.Item class="cursor-pointer" onclick={() => (createFolder = true)}>
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

			<Sidebar.Root>
				<Sidebar.Group>
					<Sidebar.Item href={localizeHref('/home')}>
						<span class="icon-[lucide--house] size-5"></span>
						{m.home()}
					</Sidebar.Item>
					<Sidebar.Item href={localizeHref('my-files')}>
						<span class="icon-[lucide--hard-drive] size-5"></span>
						{m.my_files()}
					</Sidebar.Item>
				</Sidebar.Group>

				<Sidebar.Group spaced>
					<Sidebar.Item href={localizeHref('/trash')}>
						<span class="icon-[lucide--trash-2] size-5"></span>
						{m.trash()}
					</Sidebar.Item>
					<div class="mt-2 flex flex-col gap-2 px-4">
						<Progress value={4} max={100} class="w-full" />
						<span class="text-sm text-muted-foreground">
							{m.available_space({ used: '4 GB', available: '15 GB' })}
						</span>
					</div>
				</Sidebar.Group>
			</Sidebar.Root>
		</aside>

		<main class="flex-1 overflow-auto pr-4 pb-6">
			<div class="h-full w-full rounded-2xl bg-white p-6">
				{@render children()}
			</div>
		</main>
	</div>
</div>

<NewFolderDialog bind:open={createFolder} />
