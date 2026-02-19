<script>
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';
	import { Button } from './ui/button';
	import { Plus, Upload} from '@lucide/svelte';
	import UploadFileOrFolderDialog from './UploadFileOrFolderDialog.svelte';

	let dropdownOpen = $state(false);
	let dialogOpen = $state(false);

	function openDialog() {
		dropdownOpen = false;
		dialogOpen = true;
	}
</script>

<DropdownMenu.Root bind:open={dropdownOpen}>
  <DropdownMenu.Trigger>
    <Button
      class="flex items-center justify-between w-32 h-12 px-4 py-2 text-base font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-md rounded-lg transition cursor-pointer"
    >
      <div class="flex items-center gap-2">
        <Plus class="size-5" />
        New
      </div>
    </Button>
  </DropdownMenu.Trigger>

  <DropdownMenu.Content class="bg-white shadow-lg rounded-md p-1">
    <DropdownMenu.Item
      onclick={openDialog}
      class="flex items-center gap-2 px-4 py-2 rounded hover:bg-gray-100 cursor-pointer"
    >
      <Upload class="size-4 text-gray-700" />
      Upload
    </DropdownMenu.Item>
  </DropdownMenu.Content>
</DropdownMenu.Root>

<UploadFileOrFolderDialog bind:dialogOpen />
