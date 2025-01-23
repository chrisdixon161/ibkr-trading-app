<template>
	<div>
		<h1>Dashboard</h1>
		<button @click="fetchAccount">Fetch Account</button>
		<pre>{{ account }}</pre>
	</div>
</template>

<script setup>
import { ref } from "vue";
import axios from "axios";

const account = ref(null);

const fetchAccount = async () => {
	try {
		const response = await axios.get("http://127.0.0.1:8000/api/account", {
			headers: {
				Authorization: `Bearer ${localStorage.getItem("authToken")}`,
			},
		});
		account.value = response.data;
	} catch (err) {
		console.error(err);
	}
};
</script>
