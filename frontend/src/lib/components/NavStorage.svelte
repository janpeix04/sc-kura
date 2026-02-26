<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { formatBytes } from '$lib/utilities/storage';
	import type { Icon } from '@lucide/svelte';
	import UploadButton from './UploadButton.svelte';
	import { Progress } from './ui/progress';
	import type { AvailableSpace } from '$lib/client';
	import { page } from '$app/state';

	let {
		items,
		availableSpace
	}: {
		items: {
			title: string;
			url: string;
			icon?: typeof Icon;
			isActive?: boolean;
			items?: {
				title: string;
				url: string;
			}[];
		}[];
		availableSpace: AvailableSpace;
	} = $props();

	const sidebar = Sidebar.useSidebar();

	let usedSpace = $derived(availableSpace.used);
	let totalSpace = $derived(availableSpace.total);
</script>

<Sidebar.Group>
	<Sidebar.Menu>
		<Sidebar.MenuItem>
			<UploadButton />
		</Sidebar.MenuItem>
	</Sidebar.Menu>
	<Sidebar.Menu class="mb-4">
		{#each items as item (item.title)}
			<Sidebar.MenuItem>
				<Sidebar.MenuButton
					tooltipContent={item.title}
					isActive={page.url.pathname === item.url}
					class="data-[active=true]:bg-[#E6E8EA]"
				>
					{#snippet child({ props })}
						<a href={item.url} {...props}>
							<item.icon />
							<span>{item.title}</span>
						</a>
					{/snippet}
				</Sidebar.MenuButton>
			</Sidebar.MenuItem>
		{/each}
	</Sidebar.Menu>
	<Sidebar.Menu>
		<Sidebar.MenuItem class={!sidebar.open ? 'px-1' : 'px-2'}>
			<Progress value={usedSpace} max={totalSpace} class="h-1" />
			<span
				class={`text-muted-foreground text-xs ${sidebar.open ? 'w-auto opacity-100' : 'w-0 opacity-0'} transition-opacity duration-200`}
				>{formatBytes(usedSpace)} of {formatBytes(totalSpace)} used</span
			>
		</Sidebar.MenuItem>
	</Sidebar.Menu>
</Sidebar.Group>
