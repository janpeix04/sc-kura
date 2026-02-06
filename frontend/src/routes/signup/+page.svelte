<script lang="ts">
    import * as Form from "$lib/components/ui/form/index";
    import { Label } from "$lib/components/ui/label/index";
    import { Input } from "$lib/components/ui/input/index";
    import {
        type SuperValidated,
        type Infer,
        superForm
    } from 'sveltekit-superforms';
    import { zod4Client } from "sveltekit-superforms/adapters";
	import { signupSchema, type SignupSchema } from "$lib/schemas/auth";
	import { toast } from "svelte-sonner";

    let { data }: { data : { form: SuperValidated<Infer<SignupSchema>>}} = $props();

    const form = superForm(data.form, {
        validators: zod4Client(signupSchema)
    });

    const { form: formData, enhance } = form;

    $effect(() => {
        if (!form || !('success' in form) || !('message' in form)) return;
        if (!form.success && form.message && typeof form.message === 'string') {
            toast.error(form.message);
        }
    })
</script>

<div class="w-full h-full bg-primary flex items-center justify-center">
    <form 
        action="?/signup" 
        method='POST' 
        class="bg-secondary w-105 rounded-3xl px-10 py-6" 
        use:enhance
    >
        <div class="text-center mb-8">
            <h2 class="font-semibold text-xl">Create an Account</h2>
        </div>
        <Form.Field {form} name='username'>
            <Form.Control>
                {#snippet children({ props })}
                    <Form.Label>Username</Form.Label>
                    <Input 
                        {...props}
                        bind:value={$formData.username}
                        type='text'
                        autocomplete='username'
                        placeholder="Your name"
                        required
                    />
                {/snippet}
            </Form.Control>
            <Form.FieldErrors />
        </Form.Field>

        <Form.Field {form} name='email'>
            <Form.Control>
                {#snippet children({ props })}
                    <Form.Label>Email</Form.Label>
                    <Input 
                        {...props}
                        bind:value={$formData.email}
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

        <Form.Field {form} name='confirm-password'>
            <Form.Control>
                {#snippet children({ props })}
                    <Form.Label>Confirm Password</Form.Label>
                    <Input 
                        {...props}
                        bind:value={$formData['confirm-password']}
                        type='password'
                        autocomplete='current-password'
                        placeholder="********"
                        required
                    />
                {/snippet}
            </Form.Control>
            <Form.FieldErrors />
        </Form.Field>
        <Form.Button class="w-full mt-8 h-11 px-2.5 cursor-pointer" type="submit">Sign up</Form.Button>
        <div class="text-sm text-center mt-6">
            <span>Already have an account? <a href="/" class="text-primary-high hover:underline hover:underline-offset-3">Log In</a></span>
        </div>
    </form>
</div>