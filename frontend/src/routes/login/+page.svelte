<script lang="ts">
    import * as Form from "$lib/components/ui/form/index";
    import { Input } from "$lib/components/ui/input/index";
    import {
        type SuperValidated,
        type Infer,
        superForm
    } from 'sveltekit-superforms';
    import { zod4Client } from "sveltekit-superforms/adapters";
	import { ORIGINS } from '$lib/schemas/types.js';
	import { toast } from 'svelte-sonner';
	import { loginSchema, type LoginSchema } from "$lib/schemas/auth";

    /* let { data } = $props(); */
    let { data }: { data : { form: SuperValidated<Infer<LoginSchema>>; origin: ORIGINS; message: string; }} = $props();

    const form = superForm(data.form, {
        validators: zod4Client(loginSchema)
    });

    const { form: formData, enhance } = form;

    $effect(() => {
        if (data.origin === ORIGINS.Signup) {
            toast.info(data.message, {duration: 8000});
        }
    })
</script>

<div class="w-full h-full bg-primary flex items-center justify-center">
    <form 
        action="?/login" 
        method='POST' 
        class="bg-secondary w-105 rounded-3xl px-10 py-6" 
        use:enhance
    >
        <div class="text-center mb-8">
            <h2 class="font-semibold text-xl">Welcome to Kura</h2>
        </div>
        <Form.Field {form} name='username'>
            <Form.Control>
                {#snippet children({ props })}
                    <Form.Label>Email</Form.Label>
                    <Input 
                        {...props}
                        bind:value={$formData.username}
                        type='email'
                        autocomplete='email'
                        placeholder="example@gmail.com"
                        required
                    />
                {/snippet}
            </Form.Control>
            <Form.FieldErrors />
        </Form.Field>

        <Form.Field {form} name='password'>
            <Form.Control>
                {#snippet children({ props })}
                    <Form.Label>Password</Form.Label>
                    <Input 
                        {...props}
                        bind:value={$formData.password}
                        type='password'
                        autocomplete='new-password'
                        placeholder="********"
                        required
                    />
                {/snippet}
            </Form.Control>
            <Form.FieldErrors />
        </Form.Field>
        <div class="text-sm text-right mt-3">
            <a href="/" class="text-primary-high hover:underline hover:underline-offset-3">
                Forgot your password?
            </a>
        </div>
        <Form.Button class="w-full mt-4 h-11 px-2.5 cursor-pointer" type="submit">Log in</Form.Button>
        <div class="text-sm text-center mt-6">
            <span>
                Don't have an account? 
                <a href="/signup" class="text-primary-high hover:underline hover:underline-offset-3">Sign up</a>
            </span>
        </div>
    </form>
</div>