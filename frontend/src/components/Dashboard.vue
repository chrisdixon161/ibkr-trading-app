<template>
	<div>
		<h1>Dashboard</h1>
		<button @click="fetchAccount">Fetch Account</button>
		<pre>{{ account }}</pre>
		<p v-if="errorMessage" style="color: red">{{ errorMessage }}</p>
	</div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const account = ref(null);
const errorMessage = ref("");
const router = useRouter();

const fetchAccount = async () => {
	const token = localStorage.getItem("authToken");

	if (!token) {
		errorMessage.value = "You need to log in first!";
		router.push("/login"); // Redirect to login page if no token is found
		return;
	}

	try {
		const response = await axios.get("http://127.0.0.1:8000/api/account", {
			headers: {
				Authorization: `Bearer ${token}`,
			},
		});

		account.value = response.data; // Display the fetched user data
		errorMessage.value = ""; // Reset error message if request is successful
	} catch (err) {
		console.error(err);
		errorMessage.value = "Failed to fetch account data. Please log in again.";
		localStorage.removeItem("authToken"); // Clear invalid token if error occurs
		router.push("/login"); // Redirect to login page
	}
};
</script>
