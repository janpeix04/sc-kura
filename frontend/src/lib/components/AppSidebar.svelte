<script lang="ts" module>
	const data = {
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
				url: '/storage/home',
				icon: House
			},
			{
				title: 'My Files',
				url: '/storage/my-files',
				icon: Folder
			},
			/* {
				title: 'Shared',
				url: '#',
				icon: Users
			},
			{
				title: 'Favourites',
				url: '#',
				icon: Star
			}, */
			{
				title: 'Trash',
				url: '/storage/trash',
				icon: Trash2
			}
		]
	};
</script>

<script lang="ts">
	import NavUser from './NavUser.svelte';
	import PlatformSwitcher from './PlatformSwitcher.svelte';
	import * as Sidebar from '$lib/components/ui/sidebar/index.js';
	import type { ComponentProps } from 'svelte';
	import NavStorage from './NavStorage.svelte';
	import type { UserPublic } from '$lib/client';
	import type { SidebarPlatform } from '$lib/schemas/types';
	import { CalendarDays, Folder, House, Server, Trash2 } from '@lucide/svelte';

	let {
		ref = $bindable(null),
		collapsible = 'icon',
		user,
		...restProps
	}: ComponentProps<typeof Sidebar.Root> & {
		user: UserPublic;
	} = $props();

	let activePlatform = $state<SidebarPlatform>(data.platforms[0]);
</script>

<Sidebar.Root {collapsible} {...restProps}>
	<Sidebar.Header>
		<PlatformSwitcher platforms={data.platforms} bind:activePlatform />
	</Sidebar.Header>
	<Sidebar.Content>
		{#if activePlatform.name === 'Kura'}
			<NavStorage items={data.navStorage} />
		{/if}
	</Sidebar.Content>
	<Sidebar.Footer>
		<NavUser {user} />
	</Sidebar.Footer>
	<Sidebar.Rail />
</Sidebar.Root>
