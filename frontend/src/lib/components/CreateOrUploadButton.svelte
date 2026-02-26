<script>
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { FilePlusCorner, FolderPlus, Plus, Upload } from '@lucide/svelte';
	import UploadFileOrFolderDialog from './UploadFileOrFolderDialog.svelte';
	import CreateFolderDialog from './CreateFolderDialog.svelte';

	let dropdownOpen = $state(false);
	let dialogOpen = $state(false);
	let createFolderDialogOpen = $state(false);

	function openDialog() {
		dropdownOpen = false;
		dialogOpen = true;
		createFolderDialogOpen = false;
	}

	function openCreateFolderDialog() {
		dropdownOpen = false;
		dialogOpen = false;
		createFolderDialogOpen = true;
	}
</script>

<DropdownMenu.Root bind:open={dropdownOpen}>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Sidebar.MenuButton
				{...props}
				class="bg-primary text-secondary hover:text-secondary hover:bg-primary-high mb-4 h-10 cursor-pointer rounded-full font-bold"
				tooltipContent="Create or upload"
			>
				<Plus class="size-5 stroke-3" />
				<span>Create or upload</span>
			</Sidebar.MenuButton>
		{/snippet}
	</DropdownMenu.Trigger>

	<DropdownMenu.Content
		side="bottom"
		align="start"
		class="bg-background w-[16rem] rounded-md p-1 shadow-lg"
	>
		<DropdownMenu.Item onclick={openCreateFolderDialog} class="cursor-pointer">
			<FolderPlus />
			New Folder
		</DropdownMenu.Item>
		<!-- <DropdownMenu.Item class="cursor-pointer">
			<FilePlusCorner />
			New File
		</DropdownMenu.Item> -->
		<DropdownMenu.Item onclick={openDialog} class="cursor-pointer">
			<Upload class="size-4 text-gray-700" />
			Upload
		</DropdownMenu.Item>
	</DropdownMenu.Content>
</DropdownMenu.Root>

<UploadFileOrFolderDialog bind:dialogOpen />
<CreateFolderDialog bind:dialogOpen={createFolderDialogOpen} />
