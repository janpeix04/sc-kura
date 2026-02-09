<script lang="ts">
    import { Input } from "$lib/components/ui/input/index";

    function handleChange(event: Event) {
        const input = event.target as HTMLInputElement;
        if (!input.files) return;

        const files = Array.from(input.files);

        files.forEach((file, i) => {
            console.log(`File ID-${i+1}:`, file);
        })
    }
</script>

<div class="w-full h-full flex flex-col justify-center items-center">
	<h1>Storage</h1>
    <Input type='file' multiple webkitdirectory onchange={handleChange}/>
    <Input type='file' multiple onchange={handleChange}/>
</div>
