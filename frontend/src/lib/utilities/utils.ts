export function getUserInitials(firstName: string, lastName: string) {
    const firstInitial = firstName[0].toUpperCase();
    const lastInitial = lastName[0].toUpperCase();
	return firstInitial + lastInitial
}


export function capitalize(text: string) {
    return text[0].toUpperCase() + text.slice(1);
}