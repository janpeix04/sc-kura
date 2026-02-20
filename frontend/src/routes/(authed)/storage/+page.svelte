<script lang="ts">
	import Button from '$lib/components/ui/button/button.svelte';
	import { Input } from '$lib/components/ui/input';
	import { STORAGE_LAYOUT } from '$lib/schemas/types';
	import { Grid2x2, Grid3x2, List, Search } from '@lucide/svelte';

	let layout: STORAGE_LAYOUT = $state(STORAGE_LAYOUT.Grid3x2);

    function handleLayout() {
        switch (layout) {
            case STORAGE_LAYOUT.Grid3x2:
                layout = STORAGE_LAYOUT.Grid2x2
                break;
            case STORAGE_LAYOUT.Grid2x2:
                layout = STORAGE_LAYOUT.List;
                break;
            default:
                layout = STORAGE_LAYOUT.Grid3x2
                break;
        }
    }
</script>

<div class="bg-tertiary-foreground flex h-full w-full">
	<main class="flex flex-1 flex-col gap-4 overflow-auto p-6">
		<div class="flex flex-row items-center justify-between">
			<div class="relative w-full max-w-124">
				<Search class="text-muted-foreground absolute top-1/2 left-4 size-5 -translate-y-1/2" />
				<Input type="text" class="w-full rounded-full pl-12" placeholder="Search..." />
			</div>

			<Button variant='outline' onclick={handleLayout} class="cursor-pointer">
				{#if layout === STORAGE_LAYOUT.Grid3x2}
					<Grid3x2 class="size-4.5" />
				{:else if layout === STORAGE_LAYOUT.Grid2x2}
					<Grid2x2 class="size-4.5" />
				{:else}
					<List class="size-4.5" />
				{/if}
			</Button>
		</div>

		<div class="bg-background flex flex-1 flex-col gap-4 rounded-lg p-4 shadow"></div>
	</main>
</div>
