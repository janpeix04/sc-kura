
<script lang="">
	import { localizeHref } from "$lib/paraglide/runtime";
	let { data } = $props();
</script>

<div class="flex gap-2">
	logged
	<a href={localizeHref('/logout')}>Logout</a>
</div>

<span>USER: {data.user.email}</span>