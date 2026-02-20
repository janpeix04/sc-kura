<script lang="ts">
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import { formatBytes } from '$lib/utilities/storage';
	import type { Icon } from '@lucide/svelte';
	import UploadButton from './UploadButton.svelte';
	import { Progress } from './ui/progress';

	let {
		items
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
	} = $props();

	const sidebar = Sidebar.useSidebar();

	let value = $state(268435456000);

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
				<Sidebar.MenuButton tooltipContent={item.title}>
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
			<Progress {value} max={1099511627776} class="h-1" />
			<span  class={`text-xs text-muted-foreground ${sidebar.open ? 'opacity-100 w-auto' : 'opacity-0 w-0'} transition-opacity duration-200`}>{formatBytes(value)} of {formatBytes(1099511627776)} used</span>
		</Sidebar.MenuItem>
	</Sidebar.Menu>
</Sidebar.Group>
