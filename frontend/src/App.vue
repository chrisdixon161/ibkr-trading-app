<template>
	<div>
		<header>
			<div class="wrapper">
				<!-- Conditionally render either Dashboard or Login based on authentication state -->
				<Dashboard v-if="isAuthenticated" :user="user" />
				<Login v-else />
			</div>
		</header>
	</div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import Dashboard from "./components/Dashboard.vue";
import Login from "./components/Login.vue";

// Track if the user is authenticated and store user data
const isAuthenticated = ref(false);
const user = ref(null);

// Check authentication status and set user data on mount
onMounted(() => {
	const token = localStorage.getItem("authToken");
	if (token) {
		isAuthenticated.value = true;

		// Decode the token to extract user info (without hitting the backend)
		const decodedToken = decodeToken(token);
		user.value = decodedToken; // Assuming token contains user info
	} else {
		isAuthenticated.value = false;
	}
});

// Function to decode the JWT token and extract user info
const decodeToken = (token) => {
	try {
		const payload = JSON.parse(atob(token.split(".")[1]));
		console.log("Decoded token payload:", payload);

		return {
			id: payload.sub,
			email: payload.email, // You can add more fields from the token payload as needed
		};
	} catch (error) {
		console.error("Invalid token:", error);
		return null;
	}
};
</script>

<style scoped>
.wrapper {
	display: flex;
	justify-content: center;
	align-items: center;
	flex-direction: column;
	height: 100vh;
}
</style>
