<template>
	<div>
		<h1>Dashboard</h1>
		<p><strong>Email:</strong> {{ user?.email }}</p>
		<p><strong>User ID:</strong> {{ user?.id }}</p>
	</div>
</template>

<script setup>
import { defineProps, ref } from "vue";

// Define props to receive user data from App.vue
const props = defineProps({
	user: Object,
});

// Simulate account balance data (could come from user data or API)
</script>

<style scoped>
h1 {
	font-size: 24px;
	margin-bottom: 16px;
}

p {
	font-size: 18px;
	margin: 8px 0;
}
</style>
