<script lang="ts" module>
	import ChartPieIcon from '@lucide/svelte/icons/chart-pie';
	import FrameIcon from '@lucide/svelte/icons/frame';
	import MapIcon from '@lucide/svelte/icons/map';
    
	const data = {
		user: {
			name: 'shadcn',
			email: 'm@example.com',
			avatar: '/avatars/shadcn.jpg'
		},
		platforms: [
			{
				name: 'Kura',
				logo: Server,
				plan: 'Storage System'
			},
			{
				name: 'Calendar',
				logo: CalendarDays,
				plan: 'Calendar'
			}
		],
		navStorage: [
			{
				title: 'Home',
				url: '#',
				icon: House,
			},
			{
				title: 'My Files',
				url: '#',
				icon: Folder,
			},
			{
				title: 'Shared',
				url: '#',
				icon: Users,
			},
			{
				title: 'Favourites',
				url: '#',
				icon: Star,
			},
            {
				title: 'Recycle Bin',
				url: '#',
				icon: Trash2,
			}
		],
		projects: [
			{
				name: 'Design Engineering',
				url: '#',
				icon: FrameIcon
			},
			{
				name: 'Sales & Marketing',
				url: '#',
				icon: ChartPieIcon
			},
			{
				name: 'Travel',
				url: '#',
				icon: MapIcon
			}
		]
	};
</script>

<script lang="ts">
	import NavProjects from './NavProjects.svelte';
	import NavUser from './NavUser.svelte';
	import PlatformSwitcher from './PlatformSwitcher.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import type { ComponentProps } from 'svelte';
	import NavStorage from './NavStorage.svelte';
	import type { UserPublic } from '$lib/client';
	import type { SidebarPlatform } from '$lib/schemas/types';
	import { CalendarDays, Folder, House, Server, Star, Trash2, Users } from '@lucide/svelte';
    
	let {
		ref = $bindable(null),
		collapsible = 'icon',
		user,
		...restProps
	}: ComponentProps<typeof Sidebar.Root> & { user: UserPublic } = $props();

	let activePlatform = $state<SidebarPlatform>(data.platforms[0]);
</script>

<Sidebar.Root {collapsible} {...restProps}>
	<Sidebar.Header>
		<PlatformSwitcher platforms={data.platforms} bind:activePlatform />
	</Sidebar.Header>
	<Sidebar.Content>
		{#if activePlatform.name === 'Kura'}
			<NavStorage items={data.navStorage} />
		{:else}
			<NavProjects projects={data.projects} />
		{/if}
	</Sidebar.Content>
	<Sidebar.Footer>
		<NavUser {user} />
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
